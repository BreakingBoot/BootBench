#!/usr/bin/env python3
"""Split a per-type CVE result set into individual records and write stats.md.

Open counterpart to the ``postprocess_bootloader_cves.py`` stage in the private
``BreakingBoot/cvedb`` repository, matching the ``--input/--output/--stats``
interface the GitHub Actions workflow drives it with.

It fixes one arithmetic bug visible in the published statistics.  In the
committed ``stats.md`` files the "Most Common Vendor" share exceeds 100% --
"Intel (125.00%)", "Dell (200.00%)", "Dell (400.00%)".  The published numbers
are reproduced exactly by dividing the leading vendor's CVE count by the
*number of distinct vendors* in that vulnerability class rather than by the
number of CVEs attributed to a vendor::

    escalation of privilege: Intel 5 / 4 distinct vendors  = 125.00%
    cwe-20:                  Dell  2 / 1 distinct vendor   = 200.00%
    cwe-119:                 Dell  4 / 1 distinct vendor   = 400.00%
    denial of service:       HP    2 / 9 distinct vendors  =  22.22%

which is a ``len(counter)`` where ``sum(counter.values())`` was meant.  This
tool divides by the vendor total, so the share is a real proportion and is
reported as "Dell (68 of 69 attributed)" to keep the denominator visible.

Usage
-----
    python3 cve_stats.py --input results/type1-results.json \
                         --output ../bootloader_cve_db/type1/cves \
                         --stats  ../bootloader_cve_db/type1/stats.md
"""

from __future__ import annotations

import argparse
import json
import shutil
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

UNKNOWN = {"", "n/a", "unknown", "none"}

# "CWE-20: Improper Input Validation" and "CWE-20 Improper Input Validation"
# are the same class but were counted separately, as were "denial of service"
# and "Denial of Service".  Normalising case and the CWE prefix merges them;
# pass --no-normalize to reproduce the original grouping.
_CWE_PREFIX = re.compile(r"^(cwe-\d+)\s*[:\-]?\s*", re.IGNORECASE)


def normalize_vuln_type(value: str) -> str:
    text = " ".join(value.split()).lower()
    return _CWE_PREFIX.sub(lambda m: m.group(1).lower() + ": ", text)


def load_results(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_index(source_dir: Path) -> dict[str, Path]:
    """Map CVE ID -> record path for a cvelistV5 checkout or a cves/ directory."""
    return {p.stem: p for p in source_dir.rglob("CVE-*.json")}


def export_records(results: dict[str, dict], out_dir: Path, clean: bool,
                   source_dir: Path | None = None) -> int:
    """Copy each referenced CVE record into ``out_dir`` as <CVE-ID>.json.

    ``results.json`` stores the absolute ``file_path`` each record was read
    from, which on the published data points into the CI runner's workspace
    (/home/.../actions-runner/_work/...) and so resolves nowhere else.  Pass
    ``--source-dir`` with a cvelistV5 checkout (or an existing ``cves/``
    directory) to resolve records by CVE ID instead.
    """
    if clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    index = build_index(source_dir) if source_dir else {}
    written = missing = 0
    for cve_id, entry in results.items():
        source = index.get(cve_id) or Path(entry.get("file_path", ""))
        if source.is_file():
            shutil.copyfile(source, out_dir / f"{cve_id}.json")
            written += 1
        else:
            missing += 1
    if missing:
        hint = "" if source_dir else " Pass --source-dir with a cvelistV5 checkout."
        print(f"[WARN] {missing} of {len(results)} source records could not be "
              f"resolved; {written} copied.{hint}")
    return written


def build_stats(results: dict[str, dict], normalize: bool = True) -> str:
    total = len(results)
    by_type: dict[str, Counter] = defaultdict(Counter)
    type_counts: Counter = Counter()
    years: Counter = Counter()

    for entry in results.values():
        raw_type = (entry.get("vuln_type") or "n/a").strip()
        vuln_type = normalize_vuln_type(raw_type) if normalize else raw_type.lower()
        type_counts[vuln_type] += 1
        vendor = (entry.get("vendor") or "").strip()
        if vendor.lower() not in UNKNOWN:
            by_type[vuln_type][vendor] += 1
        published = entry.get("published_date") or ""
        if len(published) >= 4 and published[:4].isdigit():
            years[published[:4]] += 1

    lines = [
        "| Vulnerability Type | Count | Percentage | Most Common Vendor |",
        "|-------------------|-------|------------|-------------------|",
    ]
    for vuln_type, count in type_counts.most_common():
        share = f"{100 * count / total:.2f}%" if total else "N/A"
        vendors = by_type.get(vuln_type)
        if vendors:
            name, hits = vendors.most_common(1)[0]
            attributed = sum(vendors.values())
            vendor_cell = f"{name} ({hits} of {attributed} attributed, {100 * hits / attributed:.2f}%)"
        else:
            vendor_cell = "N/A"
        lines.append(f"| {vuln_type} | {count} | {share} | {vendor_cell} |")

    lines += ["|||||", f"| **Total** | **{total}** | N/A | N/A |", ""]

    # The table above groups on the free-text vuln_type the CVE record carries,
    # which is inconsistent across assigners. The two below use the structured
    # fields, and are what analysis should lean on.
    cwes: Counter = Counter()
    severities: Counter = Counter()
    vectors: Counter = Counter()
    scored = 0
    for entry in results.values():
        for cwe in entry.get("cwe_ids") or []:
            cwes[cwe] += 1
        cvss = entry.get("cvss") or {}
        if cvss.get("severity"):
            severities[cvss["severity"]] += 1
            scored += 1
        vector = cvss.get("vector") or ""
        if "AV:" in vector:
            vectors[vector.split("AV:")[1][0]] += 1

    if cwes:
        with_cwe = sum(1 for e in results.values() if e.get("cwe_ids"))
        lines += ["### CWE Breakdown", "",
                  f"{with_cwe} of {total} CVEs carry a CWE.", "",
                  "| CWE | Count | Percentage |", "|-----|-------|------------|"]
        for cwe, count in cwes.most_common(20):
            lines.append(f"| {cwe} | {count} | {100 * count / with_cwe:.2f}% |")
        lines.append("")

    if severities:
        order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"]
        names = {"N": "Network", "A": "Adjacent", "L": "Local", "P": "Physical"}
        lines += ["### CVSS Severity", "",
                  f"{scored} of {total} CVEs carry a CVSS score.", "",
                  "| Severity | Count |", "|----------|-------|"]
        for level in order:
            if severities.get(level):
                lines.append(f"| {level} | {severities[level]} |")
        lines += ["", "### Attack Vector", "", "| Vector | Count |", "|--------|-------|"]
        for code, count in vectors.most_common():
            lines.append(f"| {names.get(code, code)} | {count} |")
        lines.append("")

    lines += ["### Year Breakdown", "| Year | Count |", "|------|-------|"]
    lines += [f"| {year} | {years[year]} |" for year in sorted(years)]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, required=True, help="<type>-results.json")
    parser.add_argument("--output", type=Path, help="directory to write per-CVE json records")
    parser.add_argument("--stats", type=Path, help="path to write the markdown statistics table")
    parser.add_argument("--source-dir", type=Path,
                        help="cvelistV5 checkout (or existing cves/ directory) to resolve "
                             "records by CVE ID, for when the recorded file_path does not exist")
    parser.add_argument("--keep", action="store_true",
                        help="do not delete the output directory before writing")
    parser.add_argument("--no-normalize", dest="normalize", action="store_false",
                        help="group vuln_type strings verbatim instead of merging "
                             "case and CWE-prefix variants")
    args = parser.parse_args()

    results = load_results(args.input)
    print(f"[INFO] {len(results)} CVEs in {args.input}")

    if args.output:
        written = export_records(results, args.output, clean=not args.keep,
                                 source_dir=args.source_dir)
        print(f"[INFO] wrote {written} records to {args.output}")

    stats = build_stats(results, normalize=args.normalize)
    if args.stats:
        args.stats.parent.mkdir(parents=True, exist_ok=True)
        args.stats.write_text(stats, encoding="utf-8")
        print(f"[INFO] statistics written to {args.stats}")
    else:
        print(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
