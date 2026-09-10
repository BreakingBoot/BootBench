# openbios

*Free IEEE 1275 Open Firmware implementation.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/openbios/openbios |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 16 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Provides a Forth interpreter and device tree, then boots a client program.

## Why it is Type 1

Type 1: it is the firmware interface itself, exposing device abstractions rather than preparing a specific OS.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/openbios
./scripts/analysis/run-tool.sh codeql openbios
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
