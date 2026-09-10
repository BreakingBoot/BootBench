# refind

*Graphical UEFI boot manager.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://git.code.sf.net/p/refind/code |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Scans partitions for boot loaders and kernels and presents a menu.

## Why it is Type 2

Type 2: a UEFI boot manager whose job is choosing and launching an OS.

## Security mechanisms

Detected in its build configuration and source:

- secure boot
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/refind
./scripts/analysis/run-tool.sh codeql refind
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
