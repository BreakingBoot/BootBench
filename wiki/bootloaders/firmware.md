# firmware

*Meshtastic device firmware.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/meshtastic/firmware |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 23 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

ESP32 and nRF52 firmware for LoRa mesh radios, including its update path.

## Why it is Type 3

Type 3: device firmware that owns the MCU from reset.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/firmware
./scripts/analysis/run-tool.sh codeql firmware
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
