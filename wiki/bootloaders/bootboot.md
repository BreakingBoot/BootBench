# bootboot

*Multi-architecture boot protocol and reference loaders.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://gitlab.com/bztsrc/bootboot |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Provides a uniform machine state to the kernel across BIOS, UEFI and RPi.

## Why it is Type 2

Type 2: implements a protocol for handing off to an OS kernel.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/bootboot
./scripts/analysis/run-tool.sh codeql bootboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
