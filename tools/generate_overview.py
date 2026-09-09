#!/usr/bin/env python3
"""Render tools/OVERVIEW.md from the analysis-runner manifest.

The manifest is the source of truth for which analysis tools run, what they
run on, and what blocks the rest. Rendering the overview from it means the
table cannot drift from the runners that actually exist.

Usage
-----
    python3 generate_overview.py --output OVERVIEW.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

INTRO = """# Bootloader analysis tools: what works, and on what

Which of the 24 tools in [`../analysis-tools/`](../analysis-tools/) run, which
bootloaders each one applies to, and what the rest need.

Run any of them with:

```bash
./scripts/analysis/run-tool.sh <tool> <target>
./scripts/analysis/run-tool.sh --list
```

Everything works through docker, so the host needs no toolchain. Results land
in `analysis-results/<tool>/<target>/`.

Generated from [`analysis_runners.json`](analysis_runners.json) by
`generate_overview.py` — edit the manifest, not this file.
"""


def render(tools: list[dict]) -> str:
    working = [t for t in tools if t["status"] == "runnable"]
    blocked = [t for t in tools if t["status"] != "runnable"]
    # "slow" means the setup works but no pass has completed; it belongs with
    # the blocked table, not with tools that produced a verified result.

    lines = [INTRO, "",
             f"## Working — {len(working)} of {len(tools)}", "",
             "| Tool | Applies to | Verified on |",
             "|------|-----------|-------------|"]
    for t in sorted(working, key=lambda x: x["name"].lower()):
        verified = t.get("verified_on", "")
        target, _, result = verified.partition(" -> ")
        cell = f"**{target}** — {result}" if result else verified
        lines.append(f"| [`{t['name']}`](../analysis-tools) | {t['applies_to']} | {cell} |")

    lines += ["", f"## Blocked — {len(blocked)}", "",
              "| Tool | Applies to | What it needs |",
              "|------|-----------|---------------|"]
    for t in sorted(blocked, key=lambda x: x["name"].lower()):
        lines.append(f"| `{t['name']}` | {t['applies_to']} | {t.get('blocker', '')} |")

    lines += ["", "## Which tool for which bootloader", "",
              "The corpus is source, so most tools need something built first.", "",
              "| You have | Use |",
              "|----------|-----|",
              "| Bootloader **source** that compiles | `codeql` |",
              "| A compiled **ELF or PE** bootloader | `angr`, `arbiter` |",
              "| A signed **.efi** (shim, GRUB, systemd-boot) | `pesign`, `fwupd`, `angr` |",
              "| A **UEFI firmware image** (OVMF, OEM dump) | `UEFITool`, `fiano`, `uefi-firmware-parser`, `uefi_retool`, `binwalk`, `chipsec`, `emba` |",
              "| A single **UEFI module** pulled from one | `fwhunt-scan`, `angr`, `efi_fuzz` |",
              "| An **Android bootloader** (LK, hboot) | `BootStomp`, `karonte` |",
              "| An **Intel ME region** | `MEAnalyzer` |",
              "",
              "To get a UEFI image out of the corpus, build OVMF from `type1/edk2` and",
              "extract its modules with `UEFITool --extract`; both are described in",
              "[`../scripts/analysis/README.md`](../scripts/analysis/README.md).",
              "",
              "## Patches", "",
              "Five tools needed code changes or a specific environment to run at all.",
              "[`../scripts/analysis/PATCHES.md`](../scripts/analysis/PATCHES.md) documents",
              "each, and the runners apply the patches automatically — the submodules are",
              "left untouched.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path, default=HERE / "analysis_runners.json")
    parser.add_argument("--output", type=Path, default=HERE / "OVERVIEW.md")
    args = parser.parse_args()

    tools = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(tools), encoding="utf-8")
    working = sum(1 for t in tools if t["status"] == "runnable")
    print(f"[INFO] {working} of {len(tools)} working -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
