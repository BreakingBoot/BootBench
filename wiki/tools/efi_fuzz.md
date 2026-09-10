# efi_fuzz

*Fuzzer for UEFI DXE drivers, built on a DXE emulator.*

| | |
|---|---|
| Category | Dynamic analysis, fuzzing and rehosting |
| Consumes | binary |
| Status | `runnable` |
| Upstream | https://github.com/Sentinel-One/efi_fuzz |
| Language | Python |

## What it does

Fuzz UEFI DXE drivers on top of the Qiling emulator.

## What it applies to

UEFI DXE and SMM drivers from EDK-II or an OEM image. Ships three worked examples.

## Verified run

Run against **smram_arbitrary_write example**: DXE driver emulated, SMM protocols initialised

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh efi_fuzz <target>

# results
ls analysis-results/efi_fuzz/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Needs patches/efi_fuzz-modernise.patch (5 fixes). Ships three worked examples.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
