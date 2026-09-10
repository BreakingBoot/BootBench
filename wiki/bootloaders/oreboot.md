# oreboot

*coreboot rewritten in Rust, with no C.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/oreboot/oreboot |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 2 naming a CVE, 130 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Performs silicon init and hands to a payload, targeting RISC-V and ARM as well as x86.

## Why it is Type 1

Type 1: same role and payload handoff as coreboot, different language.

## Security mechanisms

Detected in its build configuration and source:

- fortify
- secure boot
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/oreboot
./scripts/analysis/run-tool.sh codeql oreboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
