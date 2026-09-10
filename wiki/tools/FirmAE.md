# FirmAE

*Arbitrated emulation; raises firmware rehosting success rates over firmadyne.*

| | |
|---|---|
| Category | Dynamic analysis, fuzzing and rehosting |
| Consumes | firmware-image |
| Status | `manual` |
| Upstream | https://github.com/pr0v3rbs/FirmAE |
| Language | Python |

## What it does

Arbitrated firmware emulation; higher success rate than firmadyne.

## What it applies to

Linux-based router and IoT firmware images. Not bootloaders.

## Running it

No runner is provided. Its download.sh and docker-init.sh do run unattended (the fcore image builds), but init.sh then does `sudo service postgresql restart` against a PostgreSQL instance on the host, which the fcore image does not contain. It also emulates Linux router firmware, so BootBench holds no target for it.

## Notes

Ships its own docker setup: ./download.sh && ./init.sh, then ./run.sh.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
