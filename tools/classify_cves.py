#!/usr/bin/env python3
"""Mine the CVE Project record set for bootloader CVEs and assign a type.

This is the open reimplementation of the ``collect_cves.py`` stage that
produced ``bootloader_cve_db``.  The original lives in the private repository
``BreakingBoot/cvedb`` (branch ``bootloaderdb``); the keyword rules it was
driven with were public only as inline arguments in that repo's GitHub Actions
workflow, so the classification could not be reviewed or rerun.

Fidelity
--------
Replaying the rules in ``bootbench_keywords`` over the published dataset
reproduces every ``type<N>-keyword-breakdown.json`` exactly -- 734 Type 1,
301 Type 2 and 122 Type 3 CVEs, with zero keyword-count differences.  Verify
with::

    python3 validate_dataset.py --root .. --check classification

One field is deliberately not reproduced.  The original emits a normalised
``vendor`` (e.g. "Supermicro" for a record whose only vendor string is "n/a"
and whose description says "SuperMicro"), which requires a vendor lookup table
that is not published.  This tool reports ``vendor`` from the CVE record and
marks unavailable values ``n/a`` rather than guessing.

Usage
-----
    python3 classify_cves.py --cvelist ./cvelistV5 --output ./results
    python3 classify_cves.py --cvelist ./cvelistV5 --output ./results --type type1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Iterator

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bootbench_keywords import (  # noqa: E402
    BOOTLOADER_TYPES,
    all_matches,
    compile_keywords,
    first_match,
)


# Distinguishes "withdrawn upstream" from "unparseable" so the two are counted
# separately rather than both vanishing as None.  Worker results cross a
# process boundary and are pickled, so this is compared by value, never by
# identity -- an unpickled sentinel is a different object.
REJECTED: dict[str, Any] = {"__rejected__": True}


def _is_rejected(value: Any) -> bool:
    return isinstance(value, dict) and value.get("__rejected__") is True



CWE_ID_PATTERN = re.compile(r"CWE-(\d+)")


def extract_cwes(containers: list[dict]) -> list[str]:
    """Structured CWE ids, falling back to one parsed out of the description.

    65% of records set cweId directly; another 2% only name the CWE in the
    free-text description, which is still better than nothing.
    """
    found: list[str] = []
    for container in containers:
        for problem in container.get("problemTypes") or []:
            for desc in problem.get("descriptions") or []:
                cwe = desc.get("cweId")
                if not cwe:
                    match = CWE_ID_PATTERN.search(desc.get("description") or "")
                    cwe = f"CWE-{match.group(1)}" if match else None
                if cwe and cwe not in found:
                    found.append(cwe)
    return found


def extract_cvss(containers: list[dict]) -> dict[str, Any]:
    """Highest-version CVSS score present, with its vector."""
    best: dict[str, Any] = {}
    for container in containers:
        for metric in container.get("metrics") or []:
            for key, value in metric.items():
                if not key.startswith("cvssV") or not isinstance(value, dict):
                    continue
                version = value.get("version") or key.removeprefix("cvssV")
                score = value.get("baseScore")
                if score is None:
                    continue
                if not best or str(version) > str(best.get("version", "")):
                    best = {"version": str(version), "base_score": score,
                            "severity": value.get("baseSeverity"),
                            "vector": value.get("vectorString")}
    return best


def extract_affected(containers: list[dict]) -> list[dict[str, str]]:
    """Every affected vendor/product pair, not just the first vendor."""
    seen: list[dict[str, str]] = []
    for container in containers:
        for entry in container.get("affected") or []:
            vendor = (entry.get("vendor") or "").strip()
            product = (entry.get("product") or "").strip()
            if not product and not vendor:
                continue
            pair = {"vendor": vendor, "product": product}
            if pair not in seen:
                seen.append(pair)
    return seen


def extract_references(containers: list[dict]) -> list[dict[str, Any]]:
    """References, keeping the tags -- 'patch' and 'vendor-advisory' matter."""
    seen: list[dict[str, Any]] = []
    urls = set()
    for container in containers:
        for ref in container.get("references") or []:
            url = ref.get("url")
            if not url or url in urls:
                continue
            urls.add(url)
            seen.append({"url": url, "tags": ref.get("tags") or []})
    return seen


def iter_cve_files(cvelist_root: Path) -> Iterator[Path]:
    """Yield every CVE record under a cvelistV5 checkout (cves/YYYY/NNxxx/)."""
    cves_dir = cvelist_root / "cves"
    search_root = cves_dir if cves_dir.is_dir() else cvelist_root
    yield from sorted(search_root.rglob("CVE-*.json"))


def parse_cve(path: Path, include_rejected: bool = False) -> dict[str, Any] | None:
    """Extract the fields the dataset records from one CVE 5.x record.

    Rejected records are skipped by default.  A rejected CVE ("DO NOT USE THIS
    CANDIDATE NUMBER") describes no vulnerability, and upstream strips its
    description, leaving nothing to classify.  The published dataset still
    carries 56 of them; see tools/README.md.
    """
    try:
        with path.open(encoding="utf-8") as handle:
            record = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None

    metadata = record.get("cveMetadata", {})
    if metadata.get("state") == "REJECTED" and not include_rejected:
        return REJECTED

    cna = record.get("containers", {}).get("cna", {})

    description = next(
        (d.get("value", "") for d in cna.get("descriptions", []) if d.get("lang", "").startswith("en")),
        "",
    )
    if not description:
        return None

    vendors = [
        v for v in (a.get("vendor") for a in cna.get("affected", []))
        if v and v.lower() != "n/a"
    ]
    vuln_types = [
        d.get("description")
        for pt in cna.get("problemTypes", [])
        for d in pt.get("descriptions", [])
        if d.get("description")
    ]

    containers = [cna] + (record.get("containers", {}).get("adp") or [])

    return {
        "cve_id": metadata.get("cveId") or path.stem,
        "description": description,
        "published_date": metadata.get("datePublished") or cna.get("datePublic") or "n/a",
        "vendor": vendors[0] if vendors else "n/a",
        "vuln_type": vuln_types[0] if vuln_types else "n/a",
        # Structured fields the record already carries. vuln_type above is free
        # text -- 320 distinct strings across the corpus, a third of them "n/a"
        # or "other" -- so these are what analysis should actually use.
        "cwe_ids": extract_cwes(containers),
        "cvss": extract_cvss(containers),
        "affected": extract_affected(containers),
        "references": extract_references(containers),
        "file_path": str(path),
    }


def classify(description: str, include, exclude) -> str | None:
    """Return the attributed include-keyword, or None if the CVE is not this type.

    Exclusion wins over inclusion, and the first include keyword in list order
    is the one credited -- both behaviours are required to reproduce the
    published keyword breakdowns.
    """
    if first_match(description, exclude) is not None:
        return None
    return first_match(description, include)


_WORKERS: dict[str, Any] = {}
_INCLUDE_REJECTED = False


def _init_worker(type_names: list[str], include_rejected: bool) -> None:
    global _INCLUDE_REJECTED
    _INCLUDE_REJECTED = include_rejected
    for name in type_names:
        include, exclude = BOOTLOADER_TYPES[name]
        _WORKERS[name] = (compile_keywords(include), compile_keywords(exclude))


def _process(path_str: str) -> tuple[str, dict[str, Any], str] | dict[str, Any] | None:
    entry = parse_cve(Path(path_str), include_rejected=_INCLUDE_REJECTED)
    if _is_rejected(entry):
        return REJECTED
    if entry is None:
        return None
    for name, (include, exclude) in _WORKERS.items():
        keyword = classify(entry["description"], include, exclude)
        if keyword is not None:
            return name, entry, keyword
    return None


def collect(cvelist_root: Path, type_names: list[str], jobs: int,
            include_rejected: bool = False) -> dict[str, dict]:
    results = {name: {} for name in type_names}
    breakdown = {name: Counter() for name in type_names}

    paths = [str(p) for p in iter_cve_files(cvelist_root)]
    if not paths:
        raise SystemExit(f"[ERROR] no CVE records found under {cvelist_root}")
    print(f"[INFO] scanning {len(paths)} CVE records with {jobs} worker(s)")

    rejected = 0
    with ProcessPoolExecutor(max_workers=jobs, initializer=_init_worker,
                             initargs=(type_names, include_rejected)) as pool:
        for outcome in pool.map(_process, paths, chunksize=256):
            if _is_rejected(outcome):
                rejected += 1
                continue
            if outcome is None:
                continue
            name, entry, keyword = outcome
            results[name][entry["cve_id"]] = entry
            breakdown[name][keyword] += 1

    if rejected:
        print(f"[INFO] skipped {rejected} record(s) withdrawn upstream "
              "(state REJECTED); pass --include-rejected to keep them")

    return {name: {"results": results[name], "breakdown": dict(breakdown[name])}
            for name in type_names}


def write_outputs(output_dir: Path, collected: dict[str, dict]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in collected.items():
        results_path = output_dir / f"{name}-results.json"
        breakdown_path = output_dir / f"{name}-keyword-breakdown.json"
        results_path.write_text(
            json.dumps(payload["results"], indent=2, ensure_ascii=False), encoding="utf-8"
        )
        breakdown_path.write_text(
            json.dumps(payload["breakdown"], indent=2), encoding="utf-8"
        )
        print(f"[INFO] {name}: {len(payload['results'])} CVEs -> {results_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cvelist", type=Path, required=True,
                        help="path to a CVEProject/cvelistV5 checkout")
    parser.add_argument("--output", type=Path, default=Path("results"),
                        help="directory for <type>-results.json and keyword breakdowns")
    parser.add_argument("--type", dest="types", action="append",
                        choices=sorted(BOOTLOADER_TYPES),
                        help="restrict to one bootloader type (repeatable; default: all)")
    parser.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1),
                        help="worker processes (default: min(8, CPU count))")
    parser.add_argument("--include-rejected", action="store_true",
                        help="also classify CVEs withdrawn upstream (state REJECTED); "
                             "they carry no description, so this only matters for "
                             "auditing a dataset that already contains them")
    parser.add_argument("--report-overlaps", action="store_true",
                        help="also report CVEs whose description matches more than one type")
    args = parser.parse_args()

    type_names = args.types or sorted(BOOTLOADER_TYPES)
    collected = collect(args.cvelist, type_names, max(1, args.jobs),
                        include_rejected=args.include_rejected)
    write_outputs(args.output, collected)

    if args.report_overlaps:
        compiled = {n: (compile_keywords(BOOTLOADER_TYPES[n][0]),
                        compile_keywords(BOOTLOADER_TYPES[n][1])) for n in type_names}
        overlaps = {}
        for name, payload in collected.items():
            for cve_id, entry in payload["results"].items():
                also = [other for other in type_names if other != name
                        and classify(entry["description"], *compiled[other]) is not None]
                if also:
                    overlaps[cve_id] = [name, *also]
        path = args.output / "type-overlaps.json"
        path.write_text(json.dumps(overlaps, indent=2), encoding="utf-8")
        print(f"[INFO] {len(overlaps)} CVEs match more than one type -> {path}")

    total = sum(len(p["results"]) for p in collected.values())
    print(f"[INFO] {total} bootloader CVEs classified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
