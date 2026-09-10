# chipsec

*Platform security assessment: SMM, SPI, Secure Boot and chipset configuration.*

| | |
|---|---|
| Category | Platform assessment and signing |
| Consumes | host |
| Status | `runnable` |
| Upstream | https://github.com/chipsec/chipsec |
| Language | Python |

## What it does

Assess platform configuration: SMM, SPI protection, Secure Boot.

## What it applies to

UEFI firmware images offline. On-target platform checks need the live machine.

## Verified run

Run against **OVMF.fd**: EFI volumes parsed offline (chipsec_util -n uefi decode)

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh chipsec <target>

# results
ls analysis-results/chipsec/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Offline image checks exist (chipsec_util) but the security value is in the on-target modules.

## Limits

Offline image decoding only. The on-target modules -- SMM, SPI protection, Secure Boot configuration -- need a kernel driver on the live platform and cannot run in a container.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
