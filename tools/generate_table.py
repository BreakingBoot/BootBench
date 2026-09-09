#!/usr/bin/env python3
"""Generate the bootloader inventory table for oss-bootloaders/README.md.

Improved successor to ``oss-bootloaders/generate_table.py``.  Changes:

* Upstream URLs come from ``.gitmodules``, so the table links to each project
  instead of leaving the link list in ``README.md`` to be maintained by hand
  and drift away from the submodule set.
* Uninitialised submodules are reported as such.  The original emitted "N/A",
  which is indistinguishable from a repository that genuinely has no commits,
  so a table generated from a non-recursive clone looked like real data.
* Commit counts and first-commit dates are included, which is the information a
  reader wants when judging how much history the commit miner had to work with.
* ``subprocess.run`` is checked.  The original caught ``CalledProcessError``
  without passing ``check=True``, so that handler could never run and git
  failures silently became "N/A".
* The type header, output path and column set are arguments rather than
  hardcoded relative directories, so the script runs from anywhere.
* Fixes the "Bootlaoder" column-header typo.

Usage
-----
    python3 generate_table.py --root ../oss-bootloaders --output ../oss-bootloaders/table.md
"""

from __future__ import annotations

import argparse
import configparser
import subprocess
import sys
from pathlib import Path

TYPE_LABELS = {
    "type1": "Type 1 - Firmware",
    "type2": "Type 2 - OS",
    "type3": "Type 3 - Monolithic",
}


def read_gitmodules(root: Path) -> dict[str, str]:
    """Map submodule path -> upstream URL."""
    path = root / ".gitmodules"
    if not path.is_file():
        return {}
    parser = configparser.ConfigParser()
    parser.read_string(path.read_text(encoding="utf-8"))
    urls = {}
    for section in parser.sections():
        if parser.has_option(section, "path") and parser.has_option(section, "url"):
            urls[parser.get(section, "path")] = parser.get(section, "url")
    return urls


def git(repo: Path, *args: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_initialized(path: Path) -> bool:
    return (path / ".git").exists()


def web_url(url: str) -> str:
    """Turn an SSH or git remote into something a browser can open."""
    if url.startswith("git@"):
        host, _, repo = url[4:].partition(":")
        url = f"https://{host}/{repo}"
    return url.removesuffix(".git") if url.endswith(".git") else url


def collect(root: Path, urls: dict[str, str]) -> list[dict[str, str]]:
    rows = []
    for type_dir in sorted(p for p in root.iterdir() if p.is_dir() and p.name.startswith("type")):
        for repo in sorted(p for p in type_dir.iterdir() if p.is_dir()):
            rel = f"{type_dir.name}/{repo.name}"
            row = {
                "type": TYPE_LABELS.get(type_dir.name, type_dir.name),
                "name": repo.name,
                "url": web_url(urls.get(rel, "")),
                "latest": "not initialized",
                "first": "-",
                "commits": "-",
            }
            if is_initialized(repo):
                row["latest"] = git(repo, "log", "-1", "--format=%cd",
                                    "--date=format:%Y-%m-%d") or "no commits"
                row["first"] = git(repo, "log", "--reverse", "--format=%cd",
                                   "--date=format:%Y-%m-%d") or ""
                row["first"] = row["first"].split("\n")[0] if row["first"] else "-"
                row["commits"] = git(repo, "rev-list", "--count", "HEAD") or "-"
            rows.append(row)
    return rows


def render(rows: list[dict[str, str]]) -> str:
    lines = ["| Type | Bootloader | Commits | First Commit | Latest Commit |",
             "|------|-----------|---------|--------------|---------------|"]
    current = None
    for row in rows:
        if current is not None and row["type"] != current:
            lines.append("| | | | | |")
        current = row["type"]
        link = f"[{row['name']}]({row['url']})" if row["url"] else row["name"]
        lines.append(f"| {row['type']} | {link} | {row['commits']} | "
                     f"{row['first']} | {row['latest']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="directory containing type1/ type2/ type3/ (default: cwd)")
    parser.add_argument("--output", type=Path, default=Path("table.md"),
                        help="markdown file to write (default: table.md)")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"[ERROR] {root} is not a directory")

    rows = collect(root, read_gitmodules(root))
    if not rows:
        raise SystemExit(f"[ERROR] no type*/ subdirectories found under {root}")

    uninitialized = [r["name"] for r in rows if r["latest"] == "not initialized"]
    if uninitialized:
        print(f"[WARN] {len(uninitialized)} of {len(rows)} submodules are not checked out; "
              "their commit data is unavailable. Run:\n"
              "       git submodule update --init --recursive", file=sys.stderr)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(rows), encoding="utf-8")
    print(f"[INFO] {len(rows)} bootloaders written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
