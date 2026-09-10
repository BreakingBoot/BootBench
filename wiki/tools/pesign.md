# pesign

*Sign and inspect PE binaries for Secure Boot.*

| | |
|---|---|
| Category | Platform assessment and signing |
| Consumes | binary |
| Status | `runnable` |
| Upstream | https://github.com/rhboot/pesign |
| Language | C |

## What it does

Sign and inspect PE binaries for Secure Boot.

## What it applies to

Signed PE bootloaders: shim, GRUB's EFI build, systemd-boot, any signed DXE module.

## Verified run

Run against **shimx64.efi**: signed by Microsoft Corporation UEFI CA 2011

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh pesign <target>

# results
ls analysis-results/pesign/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Reports Authenticode signatures via sbverify and pesign.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
