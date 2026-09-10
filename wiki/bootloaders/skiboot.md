# skiboot

*OPAL firmware for OpenPOWER.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/open-power/skiboot |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 58 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Loaded by hostboot, provides OPAL runtime services and boots a Linux kernel via petitboot.

## Why it is Type 2

Type 2: it starts from hostboot's initialised state and prepares an OS.

## Security mechanisms

Detected in its build configuration and source:

- cfi
- encryption
- measured boot
- rollback protection
- secure boot
- signature verification
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/skiboot
./scripts/analysis/run-tool.sh codeql skiboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
