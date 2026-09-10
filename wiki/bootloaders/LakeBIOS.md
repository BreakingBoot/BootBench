# LakeBIOS

*Minimal experimental x86 BIOS implementation.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/AtieP/LakeBIOS |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Brings up a QEMU-class machine and provides a minimal BIOS interface.

## Why it is Type 1

Type 1: firmware-level bring-up from reset.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/LakeBIOS
./scripts/analysis/run-tool.sh codeql LakeBIOS
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
