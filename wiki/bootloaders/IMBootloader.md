# IMBootloader

*IMProject bootloader for STM32.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/IMProject/IMBootloader |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

CRC-checked firmware update over UART or USB, then application start.

## Why it is Type 3

Type 3: reset to application.

## Security mechanisms

Detected in its build configuration and source:

- encryption
- signature verification

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/IMBootloader
./scripts/analysis/run-tool.sh codeql IMBootloader
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
