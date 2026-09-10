# bootloader

*rust-osdev/bootloader, a Rust x86_64 kernel loader.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/rust-osdev/bootloader |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Loads a Rust kernel from BIOS or UEFI and sets up paging before handoff.

## Why it is Type 2

Type 2: it starts from an initialised platform and prepares a kernel.

## Security mechanisms

Detected in its build configuration and source:

- rollback protection
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/bootloader
./scripts/analysis/run-tool.sh codeql bootloader
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
