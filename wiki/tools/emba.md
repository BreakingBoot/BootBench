# emba

*Firmware analysis orchestrator; runs extraction and many checks in one pass.*

| | |
|---|---|
| Category | Dynamic analysis, fuzzing and rehosting |
| Consumes | firmware-image |
| Status | `runnable` |
| Upstream | https://github.com/e-m-b-a/emba |
| Language | Shell |

## What it does

Orchestrates extraction and a large battery of firmware checks.

## What it applies to

Whole firmware images, UEFI or Linux-based embedded. Broad rather than bootloader-specific.

## Verified run

Run against **OVMF.fd**: full scan, HTML report generated

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh emba <target>

# results
ls analysis-results/emba/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Needs installer.sh -g -f run once against the checkout (~4 GB), config/gh_action, and the -i flag.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
