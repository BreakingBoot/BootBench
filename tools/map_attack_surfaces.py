#!/usr/bin/env python3
"""Map CVEs and vulnerability-fixing commits onto the SoK's attack surfaces.

The paper defines six surfaces and argues the whole taxonomy in terms of them,
but nothing in the dataset records which surface an entry belongs to. This adds
that field, so "every remote-access bug in a Type 2 bootloader" becomes a
filter rather than a reading exercise.

The six, most specific first:

| | | |
|---|---|---|
| `SAS3` | software | Post-boot features -- SMM, SMI handlers, runtime services |
| `SAS1` | software | Remote access -- PXE, TFTP, DHCP, HTTP boot, iSCSI |
| `SAS4` | software | Boot-time features -- shells, boot menus, recovery modes |
| `SAS2` | software | Persistent data sources -- variables, config files, images |
| `HAS2` | hardware | External hardware -- USB, DMA, PCIe, removable media |
| `HAS1` | hardware | Invasive hardware -- SPI flash, JTAG, glitching |

Order matters: an SMI handler bug is post-boot, not merely "a firmware bug", so
the first matching surface is the primary one. Every match is kept, and the
matched text is recorded so a classification can be checked rather than
trusted.

Usage
-----
    python3 map_attack_surfaces.py --root ..            # dry run
    python3 map_attack_surfaces.py --root .. --write
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bootbench_keywords import compile_attack_surfaces  # noqa: E402

TYPES = ("type1", "type2", "type3")


def classify(text: str, surfaces) -> list[dict[str, str]]:
    """Every surface whose vocabulary appears, most specific first."""
    hits = []
    for surface_id, kind, label, pattern in surfaces:
        match = pattern.search(text)
        if match:
            hits.append({"surface": surface_id, "kind": kind, "label": label,
                         "matched": match.group(0).strip().lower()})
    return hits


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=here.parent)
    parser.add_argument("--write", action="store_true",
                        help="store the attack_surfaces field in both datasets")
    args = parser.parse_args()

    root = args.root.resolve()
    surfaces = compile_attack_surfaces()

    # --- CVEs -------------------------------------------------------------
    cve_primary: Counter = Counter()
    cve_any: Counter = Counter()
    cve_total = cve_hit = 0
    by_type: dict[str, Counter] = {t: Counter() for t in TYPES}

    for btype in TYPES:
        path = root / "bootloader_cve_db" / btype / f"{btype}-results.json"
        results = json.loads(path.read_text(encoding="utf-8"))
        for entry in results.values():
            cve_total += 1
            hits = classify(entry.get("description", ""), surfaces)
            entry["attack_surfaces"] = hits
            if hits:
                cve_hit += 1
                cve_primary[hits[0]["surface"]] += 1
                by_type[btype][hits[0]["surface"]] += 1
                for h in hits:
                    cve_any[h["surface"]] += 1
        if args.write:
            path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")

    # --- commits ----------------------------------------------------------
    commit_primary: Counter = Counter()
    commit_total = commit_hit = 0
    for path_str in sorted(glob.glob(str(root / "bootloader_vuln_commits" / "type*" / "*.json"))):
        path = Path(path_str)
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for bucket in ("CVEs", "vulnerability"):
            for entry in data.get(bucket, []):
                commit_total += 1
                hits = classify(entry.get("message", ""), surfaces)
                entry["attack_surfaces"] = hits
                changed = True
                if hits:
                    commit_hit += 1
                    commit_primary[hits[0]["surface"]] += 1
        if args.write and changed:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")

    labels = {s[0]: s[2] for s in surfaces}
    print(f"  CVEs    : {cve_hit:,} of {cve_total:,} map to a surface "
          f"({100 * cve_hit / cve_total:.0f}%)")
    print(f"  commits : {commit_hit:,} of {commit_total:,} "
          f"({100 * commit_hit / commit_total:.0f}%)")
    print("\n  primary surface, CVEs:")
    for surface, count in cve_primary.most_common():
        print(f"    {surface}  {count:5d}  {labels[surface]}")
    print("\n  primary surface, commits:")
    for surface, count in commit_primary.most_common():
        print(f"    {surface}  {count:5d}  {labels[surface]}")
    print("\n  CVEs by bootloader type and primary surface:")
    header = "         " + "".join(f"{s:>7}" for s in labels)
    print(header)
    for btype in TYPES:
        row = "".join(f"{by_type[btype].get(s, 0):>7}" for s in labels)
        print(f"    {btype}{row}")
    if not args.write:
        print("\n  dry run; pass --write to store the field")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
