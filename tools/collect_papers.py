#!/usr/bin/env python3
"""Collect bootloader-related papers from the venues the SoK surveyed.

This is the literature-search stage of BootBench.  The SoK examined the top
four security venues (IEEE S&P, ACM CCS, USENIX Security, NDSS) and four
software-engineering venues (ICSE, FSE, ASE, OOPSLA) for tools and techniques
applicable to bootloaders, using top4grep [1] to grep conference proceedings.

This tool does the same search against the same source top4grep uses -- dblp's
SPARQL endpoint -- with two differences that matter here:

* It covers all eight venues.  top4grep is hardcoded to the four security
  conferences, so the software-engineering half of the SoK's survey (where the
  general-purpose static-analysis and fuzzing tools come from) is out of its
  reach.
* It needs only the standard library.  top4grep requires ``requests`` and
  ``sqlalchemy``, and builds a local sqlite database first.

If you already have a top4grep database, ``--from-top4grep <papers.db>`` reads
it instead of querying the network, so results can be reproduced from a fixed
snapshot.

[1] https://github.com/Kyle-Kyle/top4grep

Usage
-----
    python3 collect_papers.py --since 2015 --output papers.json --markdown papers.md
    python3 collect_papers.py --venue "IEEE S&P" --venue NDSS --core-only
    python3 collect_papers.py --from-top4grep ~/top4grep/top4grep/data/papers.db
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bootbench_keywords import (  # noqa: E402
    PAPER_CONTRIBUTION_FALLBACK,
    PAPER_CONTRIBUTIONS,
    PAPER_KEYWORDS_CONTEXT,
    PAPER_KEYWORDS_CORE,
    PAPER_VENUES,
    SECURITY_VENUES,
    SE_VENUES,
    compile_keywords,
)

SPARQL_ENDPOINT = "https://sparql.dblp.org/sparql"
PREFIXES = """PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""


def sparql(query: str, timeout: int = 180) -> list[dict[str, Any]]:
    url = SPARQL_ENDPOINT + "?" + urllib.parse.urlencode(
        {"query": PREFIXES + query, "format": "application/sparql-results+json"})
    request = urllib.request.Request(
        url, headers={"Accept": "application/sparql-results+json",
                      "User-Agent": "bootbench-collect-papers"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)["results"]["bindings"]


def fetch_venue(venue: str, stream: str, since: int) -> list[dict[str, Any]]:
    """Fetch every inproceedings title for one venue since ``since``."""
    # yearOfPublication is xsd:gYear; xsd:integer(?y) matches nothing, so the
    # cast has to go through str().
    query = f"""SELECT DISTINCT ?title ?year ?url WHERE {{
  ?publ dblp:publishedInStream <https://dblp.org/streams/{stream}> ;
        rdf:type dblp:Inproceedings ;
        dblp:title ?title ;
        dblp:yearOfPublication ?year .
  OPTIONAL {{ ?publ dblp:primaryDocumentPage ?url . }}
  FILTER(xsd:integer(str(?year)) >= {since})
}}"""
    rows = sparql(query)
    return [{"title": " ".join(r["title"]["value"].split()).rstrip("."),
             "year": int(r["year"]["value"]),
             "venue": venue,
             "url": r.get("url", {}).get("value", "")}
            for r in rows]


def read_top4grep(db_path: Path, since: int) -> list[dict[str, Any]]:
    """Read papers out of a top4grep sqlite database."""
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        rows = conn.execute(
            "SELECT conference, year, title FROM paper WHERE year >= ?", (since,)
        ).fetchall()
    return [{"title": " ".join(t.split()).rstrip("."), "year": int(y),
             "venue": c, "url": ""} for c, y, t in rows]


def classify_contribution(title: str) -> tuple[str, str]:
    """Decide what a paper contributes, first matching rule wins."""
    lowered = title.lower()
    for key, label, terms in PAPER_CONTRIBUTIONS:
        if any(re.search(r"\b" + re.escape(t), lowered) for t in terms):
            return key, label
    return PAPER_CONTRIBUTION_FALLBACK


def match(papers: Iterable[dict], core_only: bool) -> list[dict[str, Any]]:
    """Keep papers whose title contains a boot-related term, recording which."""
    core = compile_keywords(PAPER_KEYWORDS_CORE, allow_plural=True)
    context = [] if core_only else compile_keywords(PAPER_KEYWORDS_CONTEXT, allow_plural=True)

    hits = []
    for paper in papers:
        title = paper["title"]
        core_hits = [k for k, p in core if p.search(title)]
        context_hits = [k for k, p in context if p.search(title)]
        if not core_hits and not context_hits:
            continue
        key, label = classify_contribution(title)
        hits.append({**paper, "matched_core": core_hits,
                     "matched_context": context_hits,
                     "tier": "core" if core_hits else "context",
                     "contribution": key, "contribution_label": label})
    hits.sort(key=lambda p: (-p["year"], p["venue"], p["title"]))
    return hits


def render_markdown(papers: list[dict], since: int, core_only: bool) -> str:
    """Group papers by what they contribute, core tier first."""
    order = [k for k, _, _ in PAPER_CONTRIBUTIONS] + [PAPER_CONTRIBUTION_FALLBACK[0]]
    labels = {k: lab for k, lab, _ in PAPER_CONTRIBUTIONS}
    labels[PAPER_CONTRIBUTION_FALLBACK[0]] = PAPER_CONTRIBUTION_FALLBACK[1]

    by_contribution: dict[str, list[dict]] = defaultdict(list)
    for paper in papers:
        by_contribution[paper["contribution"]].append(paper)

    core = [p for p in papers if p["tier"] == "core"]
    lines = [
        "# Bootloader papers, by contribution", "",
        f"{len(papers)} papers matched from {len({p['venue'] for p in papers})} venues, "
        f"{since} onwards. {len(core)} name the boot chain in their title (**core**); "
        f"the rest matched a broader firmware or embedded-systems term (**context**) and "
        "are the literature the SoK's tool survey draws on.", "",
        "Regenerate with:", "",
        "```bash",
        f"python3 tools/collect_papers.py --since {since}"
        f"{' --core-only' if core_only else ''} \\",
        "    --output papers.json --markdown PAPERS.md",
        "```", "",
        "Contribution is assigned from the title by the ordered rules in "
        "[`tools/bootbench_keywords.py`](tools/bootbench_keywords.py) "
        "(`PAPER_CONTRIBUTIONS`), first match wins.", "",
        "## Contents", "",
    ]
    for key in order:
        if by_contribution.get(key):
            anchor = labels[key].lower().replace(" ", "-").replace(",", "")
            lines.append(f"- [{labels[key]}](#{anchor}) — {len(by_contribution[key])}")
    lines.append("")

    for key in order:
        group = by_contribution.get(key)
        if not group:
            continue
        lines += [f"## {labels[key]}", ""]
        for tier in ("core", "context"):
            tiered = [p for p in group if p["tier"] == tier]
            if not tiered:
                continue
            lines += [f"**{tier.capitalize()}** ({len(tiered)})", "",
                      "| Year | Venue | Title | Matched |",
                      "|------|-------|-------|---------|"]
            for paper in sorted(tiered, key=lambda p: (-p["year"], p["venue"])):
                title = paper["title"].replace("|", "\\|")
                link = f"[{title}]({paper['url']})" if paper["url"] else title
                terms = ", ".join(f"`{t}`" for t in
                                  (paper["matched_core"] or paper["matched_context"])[:3])
                lines.append(f"| {paper['year']} | {paper['venue']} | {link} | {terms} |")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", type=int, default=2015,
                        help="earliest publication year (default: 2015)")
    parser.add_argument("--venue", dest="venues", action="append",
                        choices=sorted(PAPER_VENUES),
                        help="restrict to one venue (repeatable; default: all eight)")
    parser.add_argument("--core-only", action="store_true",
                        help="match only terms that name the boot chain directly, "
                             "dropping the broader firmware/embedded terms")
    parser.add_argument("--from-top4grep", type=Path,
                        help="read papers from a top4grep sqlite database instead of dblp")
    parser.add_argument("--output", type=Path, default=Path("papers.json"),
                        help="JSON output path (default: papers.json)")
    parser.add_argument("--markdown", type=Path,
                        help="also write a grouped markdown table here")
    args = parser.parse_args()

    if args.from_top4grep:
        if not args.from_top4grep.is_file():
            raise SystemExit(f"[ERROR] {args.from_top4grep} not found")
        print(f"[INFO] reading {args.from_top4grep}")
        papers = read_top4grep(args.from_top4grep, args.since)
        print(f"[INFO] {len(papers)} papers from the top4grep database")
    else:
        venues = args.venues or sorted(PAPER_VENUES)
        papers = []
        for venue in venues:
            try:
                found = fetch_venue(venue, PAPER_VENUES[venue], args.since)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                print(f"[ERROR] {venue}: {exc}; skipping")
                continue
            print(f"[INFO] {venue}: {len(found)} papers since {args.since}")
            papers.extend(found)
        if not papers:
            raise SystemExit("[ERROR] no papers retrieved; dblp may be unreachable. "
                             "Use --from-top4grep with a local database instead.")

    hits = match(papers, args.core_only)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(hits, indent=2, ensure_ascii=False), encoding="utf-8")

    tiers = Counter(p["tier"] for p in hits)
    print(f"[INFO] {len(hits)} of {len(papers)} papers matched "
          f"({tiers['core']} core, {tiers['context']} context) -> {args.output}")

    if args.markdown:
        args.markdown.write_text(render_markdown(hits, args.since, args.core_only),
                                 encoding="utf-8")
        print(f"[INFO] markdown written to {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
