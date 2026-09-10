# STM32duino-bootloader

*USB DFU bootloader for STM32F1 boards.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/rogerclarkmelbourne/STM32duino-bootloader |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Enumerates as a DFU device for upload, then jumps to the sketch.

## Why it is Type 3

Type 3: reset to application.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/STM32duino-bootloader
./scripts/analysis/run-tool.sh codeql STM32duino-bootloader
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
