#!/usr/bin/env python3
"""Consistency checks for the BootBench dataset.

Run from a BootBench checkout with the three data submodules initialised::

    python3 validate_dataset.py --root ..
    python3 validate_dataset.py --root .. --check classification

Checks
------
classification  Replays the keyword rules in ``bootbench_keywords`` over each
                published ``type<N>-results.json`` and compares the resulting
                attribution against the committed ``type<N>-keyword-breakdown``.
cves            Confirms each ``cves/`` directory holds one record per entry in
                the matching results file.
records         Flags CVEs counted under more than one bootloader type, and CVEs
                that upstream has since withdrawn (state REJECTED) but that are
                still counted in the dataset totals.
stats           Confirms the vulnerability-type rows in each ``stats.md`` sum to
                the total the same file states.
coverage        Cross-checks ``oss-bootloaders/.gitmodules`` against the
                directories on disk and the repositories the commit miner
                actually produced output for.
commits         Checks the mined commit records: that the summary covers every
                per-repo file, and that parent links point backwards in time
                (the legacy ``previous_commit`` field points forwards).

Exit status is non-zero if any check fails.
"""

from __future__ import annotations

import argparse
import configparser
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bootbench_keywords import BOOTLOADER_TYPES, compile_keywords, first_match  # noqa: E402

TYPES = ("type1", "type2", "type3")


class Report:
    def __init__(self) -> None:
        self.failures = 0

    def ok(self, message: str) -> None:
        print(f"  \033[32mPASS\033[0m {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        print(f"  \033[31mFAIL\033[0m {message}")

    def note(self, message: str) -> None:
        print(f"  \033[33mNOTE\033[0m {message}")


def check_classification(root: Path, report: Report) -> None:
    print("classification: keyword rules vs published breakdown")
    db = root / "bootloader_cve_db"
    for name in TYPES:
        results_path = db / name / f"{name}-results.json"
        breakdown_path = db / name / f"{name}-keyword-breakdown.json"
        if not results_path.is_file() or not breakdown_path.is_file():
            report.note(f"{name}: dataset files missing (submodule not initialised?)")
            continue
        results = json.loads(results_path.read_text(encoding="utf-8"))
        published = json.loads(breakdown_path.read_text(encoding="utf-8"))
        include = compile_keywords(BOOTLOADER_TYPES[name][0])
        exclude = compile_keywords(BOOTLOADER_TYPES[name][1])

        replayed: dict[str, int] = {}
        unmatched = 0
        for entry in results.values():
            keyword = first_match(entry.get("description", ""), include)
            if keyword is None:
                unmatched += 1
            else:
                replayed[keyword] = replayed.get(keyword, 0) + 1

        drift = sum(abs(replayed.get(k, 0) - published.get(k, 0))
                    for k in set(replayed) | set(published))
        if drift == 0 and unmatched == 0:
            report.ok(f"{name}: {len(results)} CVEs reproduce the published breakdown exactly")
        else:
            report.fail(f"{name}: {drift} keyword-count difference(s), {unmatched} unmatched CVEs")
            for key in sorted(set(replayed) | set(published)):
                if replayed.get(key, 0) != published.get(key, 0):
                    report.note(f"    {key!r}: replay={replayed.get(key, 0)} "
                                f"published={published.get(key, 0)}")

        # The breakdown only exercises include keywords.  A published CVE that
        # its own type's exclude list rejects would mean the exclude list here
        # does not match the one that built the dataset.
        rejected = [cve_id for cve_id, entry in results.items()
                    if first_match(entry.get("description", ""), exclude) is not None]
        if rejected:
            report.fail(f"{name}: exclude list rejects {len(rejected)} of its own "
                        f"published CVEs, e.g. {', '.join(sorted(rejected)[:3])}")
        else:
            report.ok(f"{name}: exclude list rejects none of its own published CVEs")


def check_cves(root: Path, report: Report) -> None:
    print("cves: record files vs results entries")
    db = root / "bootloader_cve_db"
    total = 0
    for name in TYPES:
        results_path = db / name / f"{name}-results.json"
        cves_dir = db / name / "cves"
        if not results_path.is_file() or not cves_dir.is_dir():
            report.note(f"{name}: dataset files missing")
            continue
        results = json.loads(results_path.read_text(encoding="utf-8"))
        on_disk = {p.stem for p in cves_dir.glob("CVE-*.json")}
        missing = set(results) - on_disk
        extra = on_disk - set(results)
        total += len(results)
        if not missing and not extra:
            report.ok(f"{name}: {len(results)} CVEs, one record each")
        else:
            report.fail(f"{name}: {len(missing)} results without a record, "
                        f"{len(extra)} records without a results entry")
    if total:
        report.ok(f"total across types: {total} CVEs")


def check_records(root: Path, report: Report) -> None:
    """Check for withdrawn CVEs and for CVEs counted under more than one type."""
    print("records: withdrawn CVEs and cross-type duplicates")
    db = root / "bootloader_cve_db"

    seen: dict[str, list[str]] = {}
    rejected: dict[str, list[str]] = {}
    total_files = 0
    for name in TYPES:
        cves_dir = db / name / "cves"
        if not cves_dir.is_dir():
            report.note(f"{name}: cves/ missing")
            continue
        for path in cves_dir.glob("CVE-*.json"):
            total_files += 1
            seen.setdefault(path.stem, []).append(name)
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                report.fail(f"{name}/{path.name}: unreadable")
                continue
            if record.get("cveMetadata", {}).get("state") == "REJECTED":
                rejected.setdefault(path.stem, []).append(name)

    if not total_files:
        return

    duplicates = {c: t for c, t in seen.items() if len(t) > 1}
    if duplicates:
        listed = ", ".join(f"{c} ({'+'.join(t)})" for c, t in sorted(duplicates.items()))
        report.fail(f"{len(duplicates)} CVE(s) counted under more than one type, so the "
                    f"per-type totals sum to {total_files} but cover {len(seen)} distinct "
                    f"CVEs: {listed}")
    else:
        report.ok(f"{len(seen)} distinct CVEs, none counted twice")

    if rejected:
        report.fail(f"{len(rejected)} of {len(seen)} CVEs ({100 * len(rejected) / len(seen):.1f}%) "
                    "have been withdrawn upstream (state REJECTED) but are still counted; "
                    "their records carry no description, only a rejection reason")
    else:
        report.ok("no withdrawn CVEs in the dataset")


def check_stats(root: Path, report: Report) -> None:
    print("stats: markdown row sums")
    db = root / "bootloader_cve_db"
    for name in TYPES:
        path = db / name / "stats.md"
        if not path.is_file():
            report.note(f"{name}: stats.md missing")
            continue
        text = path.read_text(encoding="utf-8")
        total_match = re.search(r"\|\s*\*\*Total\*\*\s*\|\s*\*\*(\d+)\*\*", text)
        if not total_match:
            report.fail(f"{name}: no total row in stats.md")
            continue
        stated = int(total_match.group(1))
        # Only the vulnerability-type table participates in this sum. stats.md
        # also carries CWE, severity, attack-vector and year tables, whose rows
        # count CVEs on different axes and legitimately do not add to the total.
        body = text[:total_match.start()]
        rows = [(label.strip(), int(count)) for label, count in
                re.findall(r"^\|\s*(?!\*\*Total|Vulnerability Type|-)([^|]+?)\s*\|\s*(\d+)\s*\|",
                           body, re.M)]
        row_sum = sum(count for _, count in rows)
        if row_sum == stated:
            report.ok(f"{name}: vulnerability-type rows sum to {stated}")
        else:
            report.fail(f"{name}: rows sum to {row_sum} but the table states {stated} "
                        f"({stated - row_sum} CVEs, {100 * (stated - row_sum) / stated:.0f}%, "
                        "are in no row)")


def check_coverage(root: Path, report: Report) -> None:
    print("coverage: submodules vs directories vs mined output")
    oss = root / "oss-bootloaders"
    gitmodules = oss / ".gitmodules"
    if not gitmodules.is_file():
        report.note("oss-bootloaders/.gitmodules missing")
        return
    parser = configparser.ConfigParser()
    parser.read_string(gitmodules.read_text(encoding="utf-8"))
    declared = {parser.get(s, "path") for s in parser.sections() if parser.has_option(s, "path")}

    on_disk = {f"{t.name}/{r.name}"
               for t in oss.iterdir() if t.is_dir() and t.name.startswith("type")
               for r in t.iterdir() if r.is_dir()}
    absent = declared - on_disk
    if absent:
        report.fail(f"{len(absent)} submodule(s) declared but with no directory: "
                    f"{', '.join(sorted(absent))}")
    else:
        report.ok(f"all {len(declared)} declared submodules have a directory")

    mined_dir = root / "bootloader_vuln_commits"
    if not mined_dir.is_dir():
        report.note("bootloader_vuln_commits missing")
        return
    mined = {f"{t.name}/{p.stem}" for t in mined_dir.iterdir()
             if t.is_dir() and t.name.startswith("type") for p in t.glob("*.json")}
    unmined = declared - mined
    stray = mined - declared
    if unmined:
        report.fail(f"{len(unmined)} submodule(s) never mined: {', '.join(sorted(unmined))}")
    else:
        report.ok("every declared submodule has mined output")
    if stray:
        report.fail(f"{len(stray)} mined file(s) with no matching submodule: "
                    f"{', '.join(sorted(stray))}")
    else:
        report.ok("no mined output without a matching submodule")


def check_commits(root: Path, report: Report) -> None:
    print("commits: summary coverage and parent-link direction")
    mined_dir = root / "bootloader_vuln_commits"
    summary_path = mined_dir / "summary.json"
    if not summary_path.is_file():
        report.note("bootloader_vuln_commits/summary.json missing")
        return
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    files = {f"{t.name}/{p.stem}": p for t in mined_dir.iterdir()
             if t.is_dir() and t.name.startswith("type") for p in t.glob("*.json")}

    absent = set(files) - set(summary)
    if absent:
        report.fail(f"{len(absent)} mined repositor{'y is' if len(absent) == 1 else 'ies are'} "
                    f"absent from summary.json (a zero row is evidence of a clean scan; "
                    f"absence is not): {', '.join(sorted(absent))}")
    else:
        report.ok(f"summary.json covers all {len(files)} mined repositories")

    legacy = forwards = backwards = total = 0
    for path in files.values():
        data = json.loads(path.read_text(encoding="utf-8"))
        for bucket in ("CVEs", "vulnerability"):
            entries = data.get(bucket, [])
            total += len(entries)
            if entries and "previous_commit" in entries[0]:
                legacy += len(entries)
            index = {e["commit"]: e for e in entries}
            for entry in entries:
                link = entry.get("parent") or entry.get("previous_commit")
                other = index.get(link) if link else None
                if other is None:
                    continue
                if other["date"] > entry["date"]:
                    forwards += 1
                elif other["date"] < entry["date"]:
                    backwards += 1

    if legacy:
        report.fail(f"{legacy} of {total} records use the legacy 'previous_commit' field; "
                    "re-mine with extract_vuln_commits.py to get real 'parent' links")
    if forwards or backwards:
        if forwards > backwards:
            report.fail(f"parent links point forwards in time in {forwards} checkable pairs "
                        f"vs {backwards} backwards -- the field is the next commit in "
                        "newest-first log order, not the parent")
        else:
            report.ok(f"parent links point backwards in {backwards} checkable pairs "
                      f"({forwards} forwards)")
    else:
        report.note("no checkable parent pairs found")


CHECKS = {
    "classification": check_classification,
    "cves": check_cves,
    "records": check_records,
    "stats": check_stats,
    "coverage": check_coverage,
    "commits": check_commits,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(".."),
                        help="BootBench checkout root (default: ..)")
    parser.add_argument("--check", action="append", choices=sorted(CHECKS),
                        help="run only this check (repeatable; default: all)")
    args = parser.parse_args()

    root = args.root.resolve()
    report = Report()
    for name in (args.check or list(CHECKS)):
        CHECKS[name](root, report)
        print()

    if report.failures:
        print(f"{report.failures} check(s) failed")
    else:
        print("all checks passed")
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
