# angr

*Binary analysis platform: symbolic execution and static analysis over stripped firmware.*

| | |
|---|---|
| Category | Static analysis |
| Consumes | binary |
| Status | `runnable` |
| Upstream | https://github.com/angr/angr |
| Language | Python |

## What it does

Load a compiled image and build a CFG; the base other angr tools sit on.

## What it applies to

Any compiled bootloader: ELF (U-Boot sandbox, kexec) or PE (shim, GRUB, any DXE module). Raw blobs need --base and --arch.

## Verified run

Run against **shimx64.efi**: 3,017 functions; OVMF MnpDxe -> CFG recovered

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh angr <target>

# results
ls analysis-results/angr/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Raw blobs need --base and --arch.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
