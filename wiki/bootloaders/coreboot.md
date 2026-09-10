# coreboot

*Open-source replacement for proprietary x86 firmware.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/coreboot/coreboot |
| CVEs attributed | 1 |
| Vulnerability-fixing commits | 1 naming a CVE, 312 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Runs from the reset vector, performs raw silicon and DRAM init, then hands control to a payload (SeaBIOS, GRUB, Linux, Tianocore) that does the OS-facing work.

## Why it is Type 1

Type 1: it starts from hardware with nothing initialised and deliberately does not load an OS itself -- the payload split is the defining Type 1 handoff.

## Attack surfaces seen in its CVEs

| Surface | | CVEs |
|---|---|---:|
| `SAS3` | Post-boot features (software) | 1 |

## Security mechanisms

Detected in its build configuration and source:

- measured boot
- rollback protection
- secure boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/coreboot
./scripts/analysis/run-tool.sh codeql coreboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
