# seabios

*Open-source legacy BIOS implementation, commonly a coreboot payload.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/coreboot/seabios |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 9 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Provides the 16-bit BIOS interrupt interface (int 10h, 13h, 15h) and loads the first sector of a boot device.

## Why it is Type 1

Type 1: it exposes the legacy firmware interface rather than preparing an OS, and chainloads a Type 2 loader from the MBR.

## Security mechanisms

Detected in its build configuration and source:

- measured boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/seabios
./scripts/analysis/run-tool.sh codeql seabios
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
