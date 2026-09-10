# chameleon

*Legacy Darwin/x86 boot loader.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/rescbr/chameleon |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 7 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

BIOS-era loader for booting macOS on generic hardware.

## Why it is Type 2

Type 2: it loads an OS from an initialised BIOS machine.

## Security mechanisms

Detected in its build configuration and source:

- encryption
- fortify

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/chameleon
./scripts/analysis/run-tool.sh codeql chameleon
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
