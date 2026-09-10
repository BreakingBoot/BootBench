# petitboot

*kexec-based bootloader for OpenPOWER.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/open-power/petitboot |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 11 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Runs in a small Linux environment, discovers boot options and kexecs the target kernel.

## Why it is Type 2

Type 2: it runs on an initialised platform and its only job is launching an OS.

## Security mechanisms

Detected in its build configuration and source:

- rollback protection
- secure boot
- signature verification

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/petitboot
./scripts/analysis/run-tool.sh codeql petitboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
