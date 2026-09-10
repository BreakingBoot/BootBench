# u-root

*Go userspace and bootloader for LinuxBoot.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/u-root/u-root |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 1 naming a CVE, 14 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Runs as an initramfs inside a Linux kernel embedded in firmware, then kexecs the target kernel.

## Why it is Type 2

Type 2: the OS-facing half of a LinuxBoot image; the firmware beneath it is Type 1.

## Security mechanisms

Detected in its build configuration and source:

- cfi
- fortify
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/u-root
./scripts/analysis/run-tool.sh codeql u-root
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
