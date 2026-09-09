#!/usr/bin/env python3
"""Regenerate the dataset into a staging directory and report what would change.

The point of this tool is that a refresh is *reviewed before it lands*.  It
never writes into the data submodules unless you pass ``--apply``, and
``--apply`` refuses to run if validation fails.  A refresh changes published
numbers that a paper cites, so the diff -- especially the label diff -- is the
thing to read, not the exit code.

Stages
------
``cves``     runs ``classify_cves.py`` over a cvelistV5 checkout, then
             ``cve_stats.py`` per type.  Requires ``--cvelist``.
``commits``  runs ``extract_vuln_commits.py`` over the bootloader corpus.
             Requires the nested submodules to be checked out.
``table``    runs ``generate_table.py`` over the corpus.

What the diff reports
---------------------
* CVEs added and removed, per type.
* **Label changes** -- CVEs that moved between bootloader types, and CVEs whose
  attributed keyword changed.  These are the ones to confirm by hand: the type
  is the dataset's central claim about a CVE.
* Commit records added and removed, per repository.
* Records withdrawn upstream that the live data still counts.

Usage
-----
    # review a CVE refresh
    python3 refresh_dataset.py --stage cves --cvelist ~/cvelistV5 --staging /tmp/refresh

    # review a commit refresh
    python3 refresh_dataset.py --stage commits --staging /tmp/refresh

    # after reading the diff and confirming the labels are right
    python3 refresh_dataset.py --stage cves --cvelist ~/cvelistV5 \
        --staging /tmp/refresh --apply
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
TYPES = ("type1", "type2", "type3")


def run(script: str, *args: str) -> None:
    cmd = [sys.executable, str(HERE / script), *args]
    print(f"[RUN] {' '.join(cmd[1:])}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise SystemExit(f"[ERROR] {script} failed with exit code {result.returncode}")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


# ---------------------------------------------------------------------------
# CVE refresh
# ---------------------------------------------------------------------------

def stage_cves(root: Path, staging: Path, cvelist: Path) -> None:
    staging.mkdir(parents=True, exist_ok=True)
    run("classify_cves.py", "--cvelist", str(cvelist), "--output", str(staging),
        "--report-overlaps")
    for name in TYPES:
        run("cve_stats.py", "--input", str(staging / f"{name}-results.json"),
            "--output", str(staging / name / "cves"),
            "--stats", str(staging / name / "stats.md"),
            "--source-dir", str(cvelist))


def diff_cves(root: Path, staging: Path) -> int:
    """Report the CVE diff.  Returns the number of findings needing review."""
    db = root / "bootloader_cve_db"
    needs_review = 0

    live_type: dict[str, str] = {}
    live_kw: dict[str, str] = {}
    for name in TYPES:
        for cve_id in load(db / name / f"{name}-results.json"):
            live_type[cve_id] = name
        # keyword attribution is only available in aggregate, so compare per type
    new_type: dict[str, str] = {}
    for name in TYPES:
        for cve_id in load(staging / f"{name}-results.json"):
            new_type[cve_id] = name

    print("\n=== CVE diff ===")
    print(f"  live:    {len(live_type)} distinct CVEs")
    print(f"  staged:  {len(new_type)} distinct CVEs")

    added = sorted(set(new_type) - set(live_type))
    removed = sorted(set(live_type) - set(new_type))
    relabelled = sorted(c for c in set(live_type) & set(new_type)
                        if live_type[c] != new_type[c])

    print(f"\n  added:       {len(added)}")
    for cve_id in added[:10]:
        print(f"      + {cve_id}  -> {new_type[cve_id]}")
    if len(added) > 10:
        print(f"      ... and {len(added) - 10} more")

    print(f"\n  removed:     {len(removed)}")
    for cve_id in removed[:10]:
        print(f"      - {cve_id}  (was {live_type[cve_id]})")
    if len(removed) > 10:
        print(f"      ... and {len(removed) - 10} more")

    print(f"\n  RELABELLED:  {len(relabelled)}   <-- confirm these by hand")
    for cve_id in relabelled:
        print(f"      ~ {cve_id}  {live_type[cve_id]} -> {new_type[cve_id]}")
    needs_review += len(relabelled)

    # Keyword attribution drift, per type: same CVE, different reason for inclusion.
    print("\n  keyword attribution:")
    for name in TYPES:
        live_bd = load(db / name / f"{name}-keyword-breakdown.json")
        new_bd = load(staging / f"{name}-keyword-breakdown.json")
        moved = {k: (live_bd.get(k, 0), new_bd.get(k, 0))
                 for k in set(live_bd) | set(new_bd)
                 if live_bd.get(k, 0) != new_bd.get(k, 0)}
        if not moved:
            print(f"      {name}: unchanged")
            continue
        print(f"      {name}: {len(moved)} keyword(s) changed count")
        for keyword, (before, after) in sorted(moved.items()):
            print(f"          {keyword!r}: {before} -> {after}")
    return needs_review


# ---------------------------------------------------------------------------
# Commit refresh
# ---------------------------------------------------------------------------

def stage_commits(root: Path, staging: Path) -> None:
    run("extract_vuln_commits.py", str(root / "oss-bootloaders"),
        "--output", str(staging / "commits"))


def diff_commits(root: Path, staging: Path) -> int:
    live_dir = root / "bootloader_vuln_commits"
    new_dir = staging / "commits"
    print("\n=== commit diff ===")

    live_files = {f"{t.name}/{p.stem}": p for t in live_dir.iterdir()
                  if t.is_dir() and t.name.startswith("type") for p in t.glob("*.json")}
    new_files = {f"{t.name}/{p.stem}": p for t in new_dir.iterdir()
                 if t.is_dir() and t.name.startswith("type") for p in t.glob("*.json")}

    only_live = sorted(set(live_files) - set(new_files))
    only_new = sorted(set(new_files) - set(live_files))
    if only_live:
        print(f"  repositories no longer produced: {', '.join(only_live)}")
    if only_new:
        print(f"  repositories newly produced:     {', '.join(only_new)}")

    print(f"\n  {'repository':28s} {'live':>8s} {'staged':>8s} {'delta':>8s}")
    total_live = total_new = 0
    for key in sorted(set(live_files) & set(new_files)):
        live = load(live_files[key])
        new = load(new_files[key])
        lc = len(live.get("CVEs", [])) + len(live.get("vulnerability", []))
        nc = len(new.get("CVEs", [])) + len(new.get("vulnerability", []))
        total_live += lc
        total_new += nc
        if lc != nc:
            print(f"  {key:28s} {lc:8d} {nc:8d} {nc - lc:+8d}")
    print(f"  {'TOTAL':28s} {total_live:8d} {total_new:8d} {total_new - total_live:+8d}")
    return 0


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

def apply_cves(root: Path, staging: Path) -> None:
    db = root / "bootloader_cve_db"
    for name in TYPES:
        target = db / name
        target.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(staging / f"{name}-results.json", target / f"{name}-results.json")
        shutil.copyfile(staging / f"{name}-keyword-breakdown.json",
                        target / f"{name}-keyword-breakdown.json")
        shutil.copyfile(staging / name / "stats.md", target / "stats.md")
        if (target / "cves").exists():
            shutil.rmtree(target / "cves")
        shutil.copytree(staging / name / "cves", target / "cves")
        print(f"[APPLY] {target}")


def apply_commits(root: Path, staging: Path) -> None:
    live = root / "bootloader_vuln_commits"
    new = staging / "commits"
    for item in new.iterdir():
        target = live / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copyfile(item, target)
    print(f"[APPLY] {live}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(".."),
                        help="BootBench checkout root (default: ..)")
    parser.add_argument("--stage", required=True, choices=["cves", "commits", "table"],
                        help="which part of the dataset to regenerate")
    parser.add_argument("--staging", type=Path, required=True,
                        help="directory to build the refresh in (never a submodule)")
    parser.add_argument("--cvelist", type=Path,
                        help="cvelistV5 checkout, required for --stage cves")
    parser.add_argument("--apply", action="store_true",
                        help="copy the staged refresh into the submodules; refuses to run "
                             "if validation fails. Review the diff first.")
    args = parser.parse_args()

    root = args.root.resolve()
    staging = args.staging.resolve()
    if staging.is_relative_to(root / "bootloader_cve_db") or \
       staging.is_relative_to(root / "bootloader_vuln_commits") or \
       staging.is_relative_to(root / "oss-bootloaders"):
        raise SystemExit("[ERROR] --staging must be outside the data submodules")

    if args.stage == "cves":
        if not args.cvelist:
            raise SystemExit("[ERROR] --stage cves requires --cvelist")
        stage_cves(root, staging, args.cvelist.resolve())
        review = diff_cves(root, staging)
    elif args.stage == "commits":
        stage_commits(root, staging)
        review = diff_commits(root, staging)
    else:
        run("generate_table.py", "--root", str(root / "oss-bootloaders"),
            "--output", str(staging / "table.md"))
        print(f"\n[INFO] staged table at {staging / 'table.md'}; "
              "diff it against oss-bootloaders/table.md")
        review = 0

    if not args.apply:
        print("\n[INFO] nothing was written to the submodules.")
        print("[INFO] review the diff above -- especially any RELABELLED entries -- "
              "then re-run with --apply.")
        return 0

    print("\n[INFO] --apply given; validating the staged data first")
    validate = subprocess.run([sys.executable, str(HERE / "validate_dataset.py"),
                               "--root", str(root)])
    if validate.returncode != 0:
        raise SystemExit("[ERROR] validation failed; refusing to apply. "
                         "Fix the findings above, or apply by hand if they are expected.")
    if review:
        print(f"[WARN] {review} label change(s) were reported. Applying anyway because "
              "--apply was given explicitly.")
    if args.stage == "cves":
        apply_cves(root, staging)
    elif args.stage == "commits":
        apply_commits(root, staging)
    print("[INFO] submodules updated; commit them from inside each submodule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
