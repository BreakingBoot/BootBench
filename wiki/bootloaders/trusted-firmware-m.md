# trusted-firmware-m

*Trusted Firmware-M, the Armv8-M secure runtime.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/TrustedFirmware-M/trusted-firmware-m |
| CVEs attributed | 2 |
| Vulnerability-fixing commits | 4 naming a CVE, 58 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Secure boot (often MCUboot-based BL2) plus the secure processing environment the non-secure application calls into.

## Why it is Type 3

Type 3: reset to application on a microcontroller.

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-787 | 1 |
| CWE-121 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- cfi
- encryption
- measured boot
- rollback protection
- secure boot
- signature verification

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/trusted-firmware-m
./scripts/analysis/run-tool.sh codeql trusted-firmware-m
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
