# openfirmware

*Mitch Bradley's original IEEE 1275 Open Firmware.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/MitchBradley/openfirmware |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 7 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Forth-based firmware providing device discovery, a device tree and a client interface for the OS loader.

## Why it is Type 1

Type 1: the canonical hardware-agnostic firmware interface.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/openfirmware
./scripts/analysis/run-tool.sh codeql openfirmware
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
