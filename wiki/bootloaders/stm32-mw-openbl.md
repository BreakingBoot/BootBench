# stm32-mw-openbl

*STMicroelectronics OpenBootLoader middleware.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/STMicroelectronics/stm32-mw-openbl |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Reimplements the STM32 system bootloader protocol in open source.

## Why it is Type 3

Type 3: the in-ROM-equivalent stage that owns the MCU from reset.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/stm32-mw-openbl
./scripts/analysis/run-tool.sh codeql stm32-mw-openbl
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
