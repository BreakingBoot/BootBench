# easyboot

*Multi-kernel boot manager built on the BOOTBOOT protocol.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://gitlab.com/bztsrc/easyboot |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Presents a menu and boots kernels in several formats.

## Why it is Type 2

Type 2: OS selection and launch.

## Security mechanisms

Detected in its build configuration and source:

- secure boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/easyboot
./scripts/analysis/run-tool.sh codeql easyboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
