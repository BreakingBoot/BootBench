# MEAnalyzer

*Analyse Intel ME/CSME/TXE firmware regions.*

| | |
|---|---|
| Category | Image inspection and reverse engineering |
| Consumes | firmware-image |
| Status | `runnable` |
| Upstream | https://github.com/platomav/MEAnalyzer |
| Language | Python |

## What it does

Analyse Intel ME/CSME/TXE regions.

## What it applies to

Intel ME/CSME/TXE regions, which sit beside the bootloader in the same flash part. Not present in OVMF.

## Verified run

Run against **OVMF.fd**: correctly reports no Intel ME region present

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh MEAnalyzer <target>

# results
ls analysis-results/MEAnalyzer/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Takes an ME region split out of a flash image, not a whole image.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
