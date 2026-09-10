# karonte

*Static taint tracking across firmware binaries and their IPC boundaries.*

| | |
|---|---|
| Category | Static analysis |
| Consumes | binary |
| Status | `runnable` |
| Upstream | https://github.com/ucsb-seclab/karonte |
| Language | Python |

## What it does

Static taint tracking across firmware binaries.

## What it applies to

Firmware binaries with multiple communicating components. Ships configs for Qualcomm LK (type2/lk).

## Verified run

Run against **Qualcomm LK (unpatched, staged from BootStomp)**: completed, tainted-path report written

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh karonte <target>

# results
ls analysis-results/karonte/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Uses badnack/karonte; run as -u karonte and source its virtualenv. Configs reference Qualcomm LK images karonte does not ship -- BootStomp does, under the same names, and the runner stages them across. Budget hours, not minutes.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
