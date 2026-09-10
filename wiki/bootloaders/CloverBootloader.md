# CloverBootloader

*Clover, an earlier macOS-focused UEFI bootloader.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/CloverHackyColor/CloverBootloader |
| CVEs attributed | 2 |
| Vulnerability-fixing commits | 0 naming a CVE, 5 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Similar role to OpenCore, with its own patching model.

## Why it is Type 2

Type 2: a UEFI application that launches an OS.

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-787 | 1 |
| CWE-125 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- aslr
- encryption
- fortify
- measured boot
- rollback protection
- secure boot
- signature verification
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/CloverBootloader
./scripts/analysis/run-tool.sh codeql CloverBootloader
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
