# slimbootloader

*Intel's lightweight, fast-boot firmware for IoT and embedded x86.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/slimbootloader/slimbootloader |
| CVEs attributed | 5 |
| Vulnerability-fixing commits | 0 naming a CVE, 21 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Stage1A/1B/2 silicon init via FSP, then launches an OS loader or payload.

## Why it is Type 1

Type 1: FSP-based silicon init with a payload handoff, the same structure as coreboot.

## Attack surfaces seen in its CVEs

| Surface | | CVEs |
|---|---|---:|
| `SAS3` | Post-boot features (software) | 1 |

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-190 | 2 |
| CWE-287 | 1 |
| CWE-693 | 1 |
| CWE-787 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- cfi
- measured boot
- rollback protection
- secure boot
- signature verification

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/slimbootloader
./scripts/analysis/run-tool.sh codeql slimbootloader
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
