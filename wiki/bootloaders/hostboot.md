# hostboot

*IBM OpenPOWER host firmware.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/open-power/hostboot |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 88 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Initialises POWER processors and memory from the service processor handoff, then loads skiboot.

## Why it is Type 1

Type 1: bare-hardware bring-up that hands off to a separate OS-facing stage.

## Security mechanisms

Detected in its build configuration and source:

- fortify
- measured boot
- rollback protection
- secure boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/hostboot
./scripts/analysis/run-tool.sh codeql hostboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
