# lk2nd

*Second-stage LK bootloader for msm8916 mainline Linux.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/msm8916-mainline/lk2nd |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 4 naming a CVE, 92 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Loads from the stock aboot and boots mainline Linux with a proper device tree.

## Why it is Type 2

Type 2: explicitly a second stage that prepares an OS.

## Security mechanisms

Detected in its build configuration and source:

- encryption
- rollback protection
- secure boot
- signature verification

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/lk2nd
./scripts/analysis/run-tool.sh codeql lk2nd
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
