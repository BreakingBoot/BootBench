# firmadyne

*Emulation-based dynamic analysis of Linux firmware images.*

| | |
|---|---|
| Category | Dynamic analysis, fuzzing and rehosting |
| Consumes | firmware-image |
| Status | `manual` |
| Upstream | https://github.com/firmadyne/firmadyne |
| Language | Shell |

## What it does

Emulate Linux firmware images for dynamic analysis.

## What it applies to

Linux-based router and IoT firmware images. Not bootloaders.

## Running it

No runner is provided. Same architecture as FirmAE and superseded by it: needs a host PostgreSQL database plus prebuilt QEMU kernels. Emulates Linux router firmware, not bootloaders.

## Notes

Needs postgres, qemu images and a populated database; superseded by FirmAE.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
