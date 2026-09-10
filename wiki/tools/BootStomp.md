# BootStomp

*Taint analysis for Android bootloaders; the first bootloader-specific detector.*

| | |
|---|---|
| Category | Static analysis |
| Consumes | source |
| Status | `runnable` |
| Upstream | https://github.com/ucsb-seclab/BootStomp |
| Language | Python |

## What it does

Taint analysis for Android bootloaders.

## What it applies to

Android bootloaders only: Qualcomm LK (type2/lk), Huawei fastboot, Nexus hboot, Xperia LK. Needs a per-image config.

## Verified run

Run against **Qualcomm LK (unpatched, bundled)**: 2 sink alerts, 2 loop alerts, 1 dereference alert

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh BootStomp <target>

# results
ls analysis-results/BootStomp/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Uses the authors' badnack/bootstomp image; run as -u angr and source /home/angr/.virtualenvs/angr. Needs a per-image config; it ships them with matching Android bootloader images.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
