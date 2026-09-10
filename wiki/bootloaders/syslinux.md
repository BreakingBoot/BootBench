# syslinux

*SYSLINUX family: SYSLINUX, ISOLINUX, PXELINUX, EXTLINUX.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://repo.or.cz/syslinux |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 25 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Boots Linux from FAT, ISO9660, network or ext filesystems, driven by a config file.

## Why it is Type 2

Type 2: configuration-driven OS loading from an initialised machine.

## Security mechanisms

Detected in its build configuration and source:

- fortify

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/syslinux
./scripts/analysis/run-tool.sh codeql syslinux
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
