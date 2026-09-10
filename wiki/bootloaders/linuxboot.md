# linuxboot

*Replaces UEFI DXE with a Linux kernel and userspace.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/linuxboot/linuxboot |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 1 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Keeps vendor PEI for silicon init, then runs Linux as the boot environment.

## Why it is Type 2

Type 2: it is the OS-loading stage layered on vendor Type 1 firmware.

## Security mechanisms

Detected in its build configuration and source:

- aslr
- fortify
- rollback protection
- secure boot
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/linuxboot
./scripts/analysis/run-tool.sh codeql linuxboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
