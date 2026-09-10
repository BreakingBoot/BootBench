# limine

*Modern multi-protocol bootloader for x86 and aarch64.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/limine-bootloader/limine |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 10 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Supports its own protocol plus Linux, Multiboot and chainloading, from BIOS or UEFI.

## Why it is Type 2

Type 2: boots from an initialised platform into an OS kernel.

## Security mechanisms

Detected in its build configuration and source:

- secure boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/limine
./scripts/analysis/run-tool.sh codeql limine
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
