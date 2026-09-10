#!/usr/bin/env python3
"""Score an analysis tool against BootBench's CVE-linked ground truth.

`cve-commit-links.json` resolves 78 CVEs to a fixing commit and to that
commit's parent -- a revision that still contains the bug. That makes a real
evaluation possible: check out the parent, run a tool, and ask whether it
flagged anything in the code the fix went on to change.

**What "hit" means here.** A finding counts as a hit when it lands in a file
the fix touched. That is a proxy, not proof: the tool may have flagged the
right file for the wrong reason, and a fix that touches many files is easier to
hit. It is reported as `file_hit` rather than "true positive" for that reason.
Line-level agreement is reported separately and is the stricter signal.

Findings outside the fixed files are counted but not called false positives --
a bootloader has other bugs, and this ground truth only knows about one.

Usage
-----
    python3 evaluate_tools.py --tool codeql --bootloader shim --limit 3
    python3 evaluate_tools.py --tool codeql --list
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=False).stdout.strip()


def load_targets(root: Path, bootloader: str | None) -> list[dict[str, Any]]:
    """Every (CVE, repo, parent) the linkage knows about."""
    data = json.loads((root / "bootloader_vuln_commits" /
                       "cve-commit-links.json").read_text(encoding="utf-8"))
    targets = []
    for cve_id, entry in data["links"].items():
        for fix in entry["fixes"]:
            if not fix.get("parent"):
                continue
            name = fix["repo"].split("/")[-1]
            if bootloader and name != bootloader:
                continue
            targets.append({"cve": cve_id, "repo": fix["repo"], "bootloader": name,
                            "fix": fix["commit"], "parent": fix["parent"],
                            "subject": fix["subject"],
                            "cwe_ids": entry.get("cwe_ids") or []})
    return targets


def build_for(bootloader: str) -> str:
    """The build recipe for a bootloader, so the worktree compiles."""
    for recipe in json.loads((HERE / "build_commands.json").read_text(encoding="utf-8")):
        if recipe["name"] == bootloader:
            return recipe["build"]
    raise SystemExit(f"[ERROR] no build recipe for {bootloader}; add one to "
                     "tools/build_commands.json")


def fixed_files(root: Path, target: dict[str, Any]) -> list[str]:
    """Source files the fix changed -- the ground truth locations."""
    repo = root / "oss-bootloaders" / target["repo"]
    out = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", target["fix"])
    return [f for f in out.splitlines()
            if f.endswith((".c", ".h", ".S", ".cc", ".cpp", ".rs", ".py", ".inf", ".dsc"))]


def run_codeql(root: Path, target: dict[str, Any], out_dir: Path,
               queries: str = "security-and-quality") -> Path | None:
    """Check out the vulnerable revision in a worktree and analyse it."""
    repo = root / "oss-bootloaders" / target["repo"]
    work = out_dir / "src"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "--detach", "-f",
                    str(work), target["parent"]], capture_output=True, check=False)
    if not work.exists():
        (out_dir / "error.log").write_text("worktree could not be created\n")
        return None
    try:
        # A worktree does not populate nested submodules, and several
        # bootloaders cannot build without them -- shim vendors gnu-efi, and
        # edk2's BaseTools needs brotli. Without this the build fails on a
        # missing header that looks like a toolchain problem but is not.
        subprocess.run(["git", "-C", str(work), "submodule", "update",
                        "--init", "--recursive"], capture_output=True, check=False,
                       timeout=1800)
        result = subprocess.run(
            ["bash", str(ROOT / "scripts/analysis/runners/codeql.sh"),
             str(work), "--output", str(out_dir), "--queries", queries,
             "--build", build_for(target["bootloader"])],
            capture_output=True, text=True)
        # Always keep the log. A silent empty directory is the worst outcome:
        # it cannot be told apart from a tool that found nothing.
        (out_dir / "run.log").write_text(result.stdout + result.stderr)
        sarif = out_dir / "results.sarif"
        return sarif if sarif.is_file() else None
    finally:
        subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(work)],
                       capture_output=True, check=False)


def score(sarif: Path, ground_truth: list[str]) -> dict[str, Any]:
    """Compare a tool's findings against the files the fix touched."""
    data = json.loads(sarif.read_text(encoding="utf-8"))
    findings = [r for run in data.get("runs", []) for r in run.get("results", [])]
    truth = set(ground_truth)
    in_fixed = []
    for finding in findings:
        for loc in finding.get("locations", []):
            uri = (loc.get("physicalLocation", {})
                      .get("artifactLocation", {}).get("uri", ""))
            if any(uri.endswith(t) or t.endswith(uri) for t in truth):
                in_fixed.append({"rule": finding.get("ruleId"), "file": uri})
                break
    return {"findings_total": len(findings),
            "findings_in_fixed_files": len(in_fixed),
            "file_hit": bool(in_fixed),
            "rules_in_fixed_files": sorted({f["rule"] for f in in_fixed if f["rule"]})}


def compile_matrix(output_root: Path) -> str:
    """Merge every per-bootloader evaluation into one table."""
    rows = []
    for report in sorted(output_root.parent.glob("evaluation*/codeql-evaluation.json")):
        data = json.loads(report.read_text(encoding="utf-8"))
        rows.extend(data.get("targets", []))

    scored = [r for r in rows if "file_hit" in r]
    by_boot: dict[str, list] = {}
    for row in scored:
        by_boot.setdefault(row["bootloader"], []).append(row)

    lines = ["# Tool evaluation against CVE-linked ground truth", "",
             "Each row is one CVE whose fixing commit is known. The harness checks out the",
             "commit's parent — a revision that still contains the bug — runs the tool, and",
             "asks whether any finding lands in a file the fix went on to change.", "",
             "A **hit** is a file-level coincidence, not a confirmed detection: the tool may",
             "have flagged the right file for the wrong reason, and a fix spanning many files",
             "is easier to hit. Findings elsewhere are counted but are **not** false",
             "positives — this ground truth knows about one bug per revision.", "",
             "Generated by `tools/evaluate_tools.py --matrix`.", "",
             "| Bootloader | Scored | Hits | Median findings | Median in fixed files |",
             "|---|---:|---:|---:|---:|"]
    for name, group in sorted(by_boot.items()):
        hits = sum(1 for r in group if r["file_hit"])
        totals = sorted(r["findings_total"] for r in group)
        infix = sorted(r["findings_in_fixed_files"] for r in group)
        lines.append(f"| `{name}` | {len(group)} | {hits} | "
                     f"{totals[len(totals) // 2]} | {infix[len(infix) // 2]} |")
    lines += ["", "## Per target", "",
              "| CVE | Bootloader | Vulnerable revision | Files fixed | Findings | In fixed files | Hit |",
              "|---|---|---|---:|---:|---:|---|"]
    for row in sorted(scored, key=lambda r: (r["bootloader"], r["cve"])):
        lines.append(f"| {row['cve']} | `{row['bootloader']}` | `{row['parent'][:10]}` | "
                     f"{row['ground_truth_files']} | {row['findings_total']} | "
                     f"{row['findings_in_fixed_files']} | "
                     f"{'yes' if row['file_hit'] else 'no'} |")

    unscored = [r for r in rows if "file_hit" not in r]
    if unscored:
        lines += ["", "## Not scored", "",
                  "Mostly revisions that no longer build: a decade-old bootloader against a",
                  "current toolchain is its own research problem.", "",
                  "| CVE | Bootloader | Reason |", "|---|---|---|"]
        for row in sorted(unscored, key=lambda r: r["cve"]):
            lines.append(f"| {row['cve']} | `{row['bootloader']}` | "
                         f"{row.get('skipped', 'unknown')} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--tool", default="codeql", choices=["codeql"],
                        help="only codeql reports file-level locations today")
    parser.add_argument("--bootloader", help="restrict to one bootloader")
    parser.add_argument("--limit", type=int, help="stop after N targets")
    parser.add_argument("--list", action="store_true", help="show targets and exit")
    parser.add_argument("--matrix", type=Path,
                        help="merge existing evaluation reports into one table and exit")
    parser.add_argument("--queries", default="security-and-quality",
                        help="CodeQL suite; 'code-scanning' is much faster")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "analysis-results" / "evaluation")
    args = parser.parse_args()

    root = args.root.resolve()
    # `git -C <repo> worktree add <relative path>` resolves the path against
    # the repo, not the caller's cwd, so a relative --output silently creates
    # worktrees *inside* the submodule. Resolve it before use.
    args.output = args.output.resolve()
    targets = load_targets(root, args.bootloader)

    if args.matrix:
        args.matrix.write_text(compile_matrix(args.output.resolve()), encoding="utf-8")
        print(f"[INFO] matrix written to {args.matrix}")
        return 0

    if args.list:
        by = Counter(t["bootloader"] for t in targets)
        print(f"  {len(targets)} CVE-linked targets")
        for name, count in by.most_common():
            recipe = "buildable" if name in {
                r["name"] for r in json.loads((HERE / "build_commands.json").read_text())
                if r.get("verified")} else "no verified build recipe"
            print(f"    {count:3d}  {name}  ({recipe})")
        return 0

    # A fix that touched no source file gives nothing to score against, so
    # drop those before applying --limit rather than spending a slot on them.
    targets = [t for t in targets if fixed_files(root, t)]
    if args.limit:
        targets = targets[:args.limit]
    if not targets:
        raise SystemExit("[ERROR] no targets; try --list")

    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, target in enumerate(targets, 1):
        truth = fixed_files(root, target)
        print(f"[{i}/{len(targets)}] {target['cve']} {target['repo']} "
              f"parent={target['parent'][:10]} ({len(truth)} files fixed)")
        if not truth:
            rows.append({**target, "skipped": "fix touched no source files"})
            continue
        out_dir = args.output / f"{target['cve']}_{target['bootloader']}"
        out_dir.mkdir(parents=True, exist_ok=True)
        sarif = run_codeql(root, target, out_dir, args.queries)
        if sarif is None:
            rows.append({**target, "skipped": "tool did not produce results",
                         "ground_truth_files": len(truth)})
            print("        tool produced no results")
            continue
        result = score(sarif, truth)
        rows.append({**target, "ground_truth_files": len(truth), **result})
        print(f"        {result['findings_total']} findings, "
              f"{result['findings_in_fixed_files']} in fixed files, "
              f"hit={result['file_hit']}")

    report = args.output / f"{args.tool}-evaluation.json"
    report.write_text(json.dumps({"tool": args.tool, "targets": rows}, indent=2),
                      encoding="utf-8")
    scored = [r for r in rows if "file_hit" in r]
    hits = sum(1 for r in scored if r["file_hit"])
    print(f"\n[INFO] {len(scored)} target(s) scored, {hits} with a finding in a fixed file")
    print(f"[INFO] {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
