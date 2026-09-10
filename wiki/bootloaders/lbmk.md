# lbmk

*Libreboot's build system, packaging coreboot with free payloads.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://codeberg.org/libreboot/lbmk |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 9 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Produces coreboot images with GRUB or SeaBIOS payloads for supported machines.

## Why it is Type 1

Type 1: a distribution of Type 1 firmware; the payload it bundles is Type 2.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/lbmk
./scripts/analysis/run-tool.sh codeql lbmk
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
