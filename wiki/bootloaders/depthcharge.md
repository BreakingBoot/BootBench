# depthcharge

*ChromeOS bootloader, a coreboot payload.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://chromium.googlesource.com/chromiumos/platform/depthcharge/ |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 18 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Implements Chrome OS verified boot, selects a kernel partition and boots it.

## Why it is Type 2

Type 2: it is the payload that coreboot (Type 1) hands off to, and it prepares an OS.

## Security mechanisms

Detected in its build configuration and source:

- measured boot
- rollback protection
- secure boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/depthcharge
./scripts/analysis/run-tool.sh codeql depthcharge
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
