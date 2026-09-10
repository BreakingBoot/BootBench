# fwhunt-scan

*Rule-based scanner for known UEFI threats and vulnerable modules.*

| | |
|---|---|
| Category | Static analysis |
| Consumes | firmware-image |
| Status | `runnable` |
| Upstream | https://github.com/binarly-io/fwhunt-scan |
| Language | Python |

## What it does

Match UEFI modules against FwHunt threat rules.

## What it applies to

Individual UEFI modules (PE32+) from EDK-II, Project Mu or an OEM image.

## Verified run

Run against **OVMF MnpDxe**: 94 boot services, 32 protocols, 11 GUIDs

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh fwhunt-scan <target>

# results
ls analysis-results/fwhunt-scan/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Analyses a single UEFI module; --rules matches against a FwHunt rule set.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
