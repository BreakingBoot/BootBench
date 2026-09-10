# arbiter

*Static and symbolic detection of the bug classes the SoK evaluates.*

| | |
|---|---|
| Category | Static analysis |
| Consumes | binary |
| Status | `runnable` |
| Upstream | https://github.com/jkrshnmenon/arbiter |
| Language | Python |

## What it does

Static and symbolic detection of specific bug classes.

## What it applies to

Compiled bootloader binaries, x86/x86-64. Needs a template naming the sinks.

## Verified run

Run against **kexec**: 10 integer-overflow findings with taint histories

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh arbiter <target>

# results
ls analysis-results/arbiter/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Needs patches/arbiter-angr-api.patch and a real template; templates/bootloader_CWE190.py targets UEFI/U-Boot/libc allocation sinks.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
