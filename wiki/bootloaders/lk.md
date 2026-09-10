# lk

*Little Kernel, a small embedded OS used as a bootloader.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/littlekernel/lk |
| CVEs attributed | 6 |
| Vulnerability-fixing commits | 1 naming a CVE, 12 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Used by Qualcomm as the Android aboot bootloader: initialises minimal hardware, verifies and boots the Android boot image.

## Why it is Type 2

Type 2 in this corpus: it runs after the SoC's primary bootloader has brought the platform up, and loads an OS. Arguably Type 3 on platforms where it is the only stage.

## Attack surfaces seen in its CVEs

| Surface | | CVEs |
|---|---|---:|
| `SAS4` | Boot-time features (software) | 1 |

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-703 | 1 |
| CWE-20 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- encryption
- rollback protection
- signature verification

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/lk
./scripts/analysis/run-tool.sh codeql lk
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
