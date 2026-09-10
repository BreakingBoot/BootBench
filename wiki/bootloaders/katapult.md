# katapult

*CAN, USB and UART bootloader for MCUs, common on 3D printer boards.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/Arksine/katapult |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 2 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Accepts firmware over its supported transports, then runs the application.

## Why it is Type 3

Type 3: reset to application.

## Security mechanisms

Detected in its build configuration and source:

- rollback protection
- secure boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/katapult
./scripts/analysis/run-tool.sh codeql katapult
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
