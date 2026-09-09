#!/usr/bin/env python3
"""Mine bootloader git histories for CVE-referencing and vulnerability-fixing commits.

Improved successor to ``bootloader_vuln_commits/extract_cve_commits.py``.  It
produces the same directory shape (``<output>/<type>/<repo>.json`` plus
``summary.json``) so it drops into the existing workflow, with four behavioural
corrections that are measured in tools/README.md:

1. ``parent`` / ``parents`` replace ``previous_commit``.  The old field was
   filled from the previous iteration of a ``git log`` walk, and ``git log`` is
   newest-first, so it pointed at a *newer* commit rather than the parent -- on
   the published data, 467 of 548 checkable adjacent pairs pointed forwards in
   time.  A vulnerability dataset needs the parent: it is the last state of the
   tree that still contains the bug.  This tool reads ``%P`` from git directly.
2. Keyword matching is word-bounded.  The original compiled word-bounded
   patterns into ``VULN_PATTERNS`` and then never used them, matching bare
   substrings instead.  1,102 of 3,377 published "vulnerability" commits
   (32.6%) were matched only that way -- "TODOs", "msdos", "FreeDOS".
3. The bare ``dos`` keyword is gone.  Even word-bounded it matched 267 commits,
   all of them about DOS the operating system ("DOS header", "dos partition
   table") and none about denial of service.
4. CWE tagging is phrase-based rather than RapidFuzz ``token_set_ratio`` at
   threshold 90.  That scorer returns 100 whenever a CWE name's tokens are a
   subset of the message's, which tagged "Bump version to 15.8" as CWE-680
   (Integer Overflow to Buffer Overflow) and "roms: only support
   SeaBIOS/SeaGRUB on x86" as CWE-260 (Password in Configuration File).

Each commit also records ``matched_keywords``, so every inclusion in the
dataset can be traced to the rule that put it there.

Usage
-----
    python3 extract_vuln_commits.py ../oss-bootloaders --output ../bootloader_vuln_commits
    python3 extract_vuln_commits.py ../oss-bootloaders --output ./out --jobs 8 --since 2015-01-01
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bootbench_keywords import (  # noqa: E402
    CVE_PATTERN,
    compile_cwe_patterns,
    compile_vulnerability_patterns,
)

FIELD_SEP = "\x1f"
# %H hash, %P parents, %aI author date, %cI commit date, %B raw body
LOG_FORMAT = FIELD_SEP.join(["%H", "%P", "%aI", "%cI", "%B"])

VULN_PATTERNS = compile_vulnerability_patterns()
CWE_PATTERNS = compile_cwe_patterns()


def is_git_repo(path: Path) -> bool:
    """True if ``path`` is a git repository (worktree, submodule or bare)."""
    return (path / ".git").exists() or (path / "HEAD").is_file()


def read_log(repo: Path, since: str | None) -> list[str] | None:
    """Return NUL-separated commit records, or None if the repo is unreadable."""
    cmd = ["git", "-C", str(repo), "log", "-z", "--no-show-signature",
           f"--pretty=format:{LOG_FORMAT}"]
    if since:
        cmd.append(f"--since={since}")
    try:
        out = subprocess.run(cmd, capture_output=True, encoding="utf-8",
                             errors="replace", check=True).stdout
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] git log failed for {repo}: {(exc.stderr or '').strip()}")
        return None
    except FileNotFoundError:
        print("[ERROR] git executable not found")
        return None
    return [rec for rec in out.split("\0") if rec.strip()]


def match_cwes(message: str) -> list[dict[str, str]]:
    """Tag a message with CWEs whose alias phrases it actually contains."""
    return [
        {"CWE-ID": cwe_id, "Name": name, "matched": match.group(0)}
        for cwe_id, name, pattern in CWE_PATTERNS
        if (match := pattern.search(message))
    ]


def scan_repo(repo_str: str, since: str | None) -> dict[str, Any]:
    """Scan one repository and return its findings plus a summary row."""
    repo = Path(repo_str)
    name = repo.name
    records = read_log(repo, since)
    if records is None:
        return {"repo": name, "error": "unreadable", "CVEs": [], "vulnerability": []}

    cve_commits: list[dict[str, Any]] = []
    vuln_commits: list[dict[str, Any]] = []

    for record in records:
        fields = record.split(FIELD_SEP, 4)
        if len(fields) < 5:
            continue
        commit_hash, parents_raw, author_date, commit_date, message = fields
        message = message.strip()
        if not message or message.startswith("Squashed"):
            continue

        cve_ids = sorted({m.group(0).upper() for m in CVE_PATTERN.finditer(message)})
        keywords = [kw for kw, pattern in VULN_PATTERNS if pattern.search(message)]
        if not cve_ids and not keywords:
            continue

        parents = parents_raw.split() if parents_raw else []
        entry: dict[str, Any] = {
            "commit": commit_hash,
            # The parent is the last revision that still contains the bug when
            # this commit is the fix.  Merge commits list every parent.
            "parent": parents[0] if parents else None,
            "parents": parents,
            "date": author_date,
            "commit_date": commit_date,
            "message": message,
        }
        if keywords:
            entry["matched_keywords"] = keywords
        cwes = match_cwes(message)
        if cwes:
            entry["CWE_matches"] = cwes

        if cve_ids:
            entry["cve_ids"] = cve_ids
            cve_commits.append(entry)
        else:
            vuln_commits.append(entry)

    return {"repo": name, "CVEs": cve_commits, "vulnerability": vuln_commits,
            "commits_scanned": len(records)}


def _worker(args: tuple[str, str, str, str | None]) -> tuple[str, str, dict[str, Any]]:
    type_dir, repo_dir, repo_path, since = args
    return type_dir, repo_dir, scan_repo(repo_path, since)


def process_tree(base: Path, output: Path, jobs: int, since: str | None) -> None:
    tasks: list[tuple[str, str, str, str | None]] = []
    skipped: list[str] = []

    for type_path in sorted(p for p in base.iterdir() if p.is_dir()):
        if not type_path.name.startswith("type"):
            continue
        for repo_path in sorted(p for p in type_path.iterdir() if p.is_dir()):
            if not is_git_repo(repo_path):
                # The published dataset contains a type1/Download.json produced
                # by scanning a directory that was never a git repository.
                skipped.append(f"{type_path.name}/{repo_path.name}")
                continue
            tasks.append((type_path.name, repo_path.name, str(repo_path), since))

    if skipped:
        print(f"[INFO] skipping {len(skipped)} non-repository director"
              f"{'y' if len(skipped) == 1 else 'ies'}: {', '.join(skipped)}")
    if not tasks:
        raise SystemExit(f"[ERROR] no git repositories found under {base}. "
                         "Run: git submodule update --init --recursive")

    print(f"[INFO] scanning {len(tasks)} repositories with {jobs} worker(s)")
    summary: dict[str, dict[str, Any]] = {}
    empty: list[str] = []

    with ProcessPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(_worker, task) for task in tasks]
        for future in as_completed(futures):
            type_dir, repo_dir, result = future.result()
            out_dir = output / type_dir
            out_dir.mkdir(parents=True, exist_ok=True)
            payload = {"CVEs": result["CVEs"], "vulnerability": result["vulnerability"]}
            (out_dir / f"{repo_dir}.json").write_text(
                json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            # Unlike the original, every scanned repo appears in the summary --
            # a zero row is evidence the repo was searched and found clean,
            # which absence cannot express.
            row = {
                "CVEs": len(result["CVEs"]),
                "vulnerabilities": len(result["vulnerability"]),
                "commits_scanned": result.get("commits_scanned", 0),
            }
            if result.get("error"):
                row["error"] = result["error"]
            summary[f"{type_dir}/{repo_dir}"] = row
            if not row["CVEs"] and not row["vulnerabilities"]:
                empty.append(f"{type_dir}/{repo_dir}")

    output.mkdir(parents=True, exist_ok=True)
    summary = dict(sorted(summary.items()))
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    total_cve = sum(r["CVEs"] for r in summary.values())
    total_vuln = sum(r["vulnerabilities"] for r in summary.values())
    print(f"[INFO] {total_cve} CVE-referencing commits, {total_vuln} keyword-matched commits")
    print(f"[INFO] {len(empty)} repositories had no findings: {', '.join(empty) or 'none'}")
    print(f"[INFO] summary written to {output / 'summary.json'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("base", type=Path,
                        help="directory containing type1/ type2/ type3/ repository trees")
    parser.add_argument("--output", "-o", type=Path, default=Path("output"),
                        help="output directory (default: ./output)")
    parser.add_argument("--jobs", "-j", type=int, default=min(8, os.cpu_count() or 1),
                        help="parallel repository scans (default: min(8, CPU count))")
    parser.add_argument("--since", help="only consider commits after this date, e.g. 2015-01-01")
    args = parser.parse_args()

    base = args.base.resolve()
    if not base.is_dir():
        raise SystemExit(f"[ERROR] {base} is not a directory")
    process_tree(base, args.output.resolve(), max(1, args.jobs), args.since)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
