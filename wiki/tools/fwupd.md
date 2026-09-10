# fwupd

*Firmware update service; the delivery side of the boot chain.*

| | |
|---|---|
| Category | Platform assessment and signing |
| Consumes | host |
| Status | `runnable` |
| Upstream | https://github.com/fwupd/fwupd |
| Language | C |

## What it does

Firmware update delivery; the write side of the boot chain.

## What it applies to

Any firmware blob, offline. Identifies the container format and hashes it as Secure Boot would.

## Verified run

Run against **shimx64.efi**: Authenticode hash and PE section layout

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh fwupd <target>

# results
ls analysis-results/fwupd/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Offline firmware-parse/-extract only; the update path needs the live platform.

## Limits

Applying an update needs a privileged daemon on real hardware.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
