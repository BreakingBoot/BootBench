#!/usr/bin/env python3
"""Render analysis-tools/README.md from tools/analysis_tools.json.

The manifest is the source of truth: it records where each tool lives, what it
does, and why it is in BootBench. This renders it, so the README cannot drift
from the submodules that are actually checked in.

Usage
-----
    python3 generate_tools_table.py --manifest analysis_tools.json \
        --output ../analysis-tools/README.md
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ORDER = ["static", "dynamic", "inspection", "platform", "survey"]

INTRO = """# Bootloader analysis tools

The tools BootBench exists to evaluate, collected as submodules so a given
version can be pinned alongside the dataset. Pointers only — no vendored code.

The SoK found that most bootloader analysis tools are tied to one
implementation and cover one attack surface: of the 25 techniques it surveyed,
only 3 covered more than one. This directory is the practical side of that
finding — what is actually available to run.

See [`tools/OVERVIEW.md`](../tools/OVERVIEW.md) for which of these run, and
what each one applies to.

```bash
git submodule update --init --recursive analysis-tools     # all of them
git submodule update --init analysis-tools/dynamic/tsffs   # or just one
```

Regenerate this file with:

```bash
python3 tools/generate_tools_table.py --output analysis-tools/README.md
```
"""


def render(tools: list[dict]) -> str:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for tool in tools:
        by_category[tool["category"]].append(tool)

    lines = [INTRO, "", "## Contents", ""]
    for key in ORDER:
        group = by_category.get(key)
        if group:
            anchor = group[0]["category_label"].lower().replace(" ", "-").replace(",", "")
            lines.append(f"- [{group[0]['category_label']}](#{anchor}) — {len(group)}")
    lines.append("")

    for key in ORDER:
        group = by_category.get(key)
        if not group:
            continue
        lines += [f"## {group[0]['category_label']}", "",
                  "| Tool | What it does | Language | Stars | Last push |",
                  "|------|--------------|----------|------:|-----------|"]
        for tool in sorted(group, key=lambda t: -(t["stars"] or 0)):
            stars = f"{tool['stars']:,}" if tool["stars"] is not None else "—"
            pushed = tool["last_push"] or "—"
            flag = " *(archived)*" if tool.get("archived") else ""
            lines.append(f"| [{tool['name']}]({tool['url']}){flag} | {tool['why']} | "
                         f"{tool['language'] or '—'} | {stars} | {pushed} |")
        lines.append("")

    lines += ["## Manifest", "",
              "[`tools/analysis_tools.json`](../tools/analysis_tools.json) drives both this "
              "file and [`scripts/add-analysis-tools.sh`](../scripts/add-analysis-tools.sh). "
              "Add an entry there, run the script, and regenerate this README.", ""]
    return "\n".join(lines)


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path, default=here / "analysis_tools.json",
                        help="tool manifest (default: tools/analysis_tools.json)")
    parser.add_argument("--output", type=Path, required=True, help="markdown file to write")
    args = parser.parse_args()

    tools = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(tools), encoding="utf-8")
    print(f"[INFO] {len(tools)} tools written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
