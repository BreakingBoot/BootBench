# mbed-bootloader

*Mbed OS bootloader with firmware update support.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/PelionIoT/mbed-bootloader |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Verifies and applies an update image, then boots the Mbed application.

## Why it is Type 3

Type 3: reset to application.

## Security mechanisms

Detected in its build configuration and source:

- rollback protection

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/mbed-bootloader
./scripts/analysis/run-tool.sh codeql mbed-bootloader
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
