# mcuboot

*Secure bootloader for 32-bit microcontrollers.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/mcu-tools/mcuboot |
| CVEs attributed | 3 |
| Vulnerability-fixing commits | 9 naming a CVE, 10 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Validates image signatures, manages primary/secondary slots, handles rollback and swap, then jumps to the application.

## Why it is Type 3

Type 3: it runs from reset on the MCU and jumps straight into the application -- there is no OS-loader stage to hand off to.

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-354 | 1 |
| CWE-121 | 1 |
| CWE-347 | 1 |

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
git -C oss-bootloaders submodule update --init type3/mcuboot
./scripts/analysis/run-tool.sh codeql mcuboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
