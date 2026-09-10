# Adafruit_nRF52_Bootloader

*UF2 and DFU bootloader for nRF52 boards.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/adafruit/Adafruit_nRF52_Bootloader |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 4 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Presents a USB mass-storage device for drag-and-drop firmware update, then starts the application.

## Why it is Type 3

Type 3: reset to application.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/Adafruit_nRF52_Bootloader
./scripts/analysis/run-tool.sh codeql Adafruit_nRF52_Bootloader
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
