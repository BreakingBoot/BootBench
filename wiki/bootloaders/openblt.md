# openblt

*Open-source bootloader for automotive and embedded MCUs.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/feaser/openblt |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Provides firmware update over CAN, USB, UART or TCP/IP, then runs the application.

## Why it is Type 3

Type 3: reset to application with an update path.

## Security mechanisms

Detected in its build configuration and source:

- encryption
- secure boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/openblt
./scripts/analysis/run-tool.sh codeql openblt
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
