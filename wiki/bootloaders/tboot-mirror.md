# tboot-mirror

*Trusted Boot, a pre-kernel module for Intel TXT measured launch.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/BreakingBoot/tboot-mirror |
| CVEs attributed | 3 |
| Vulnerability-fixing commits | 0 naming a CVE, 19 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Performs a measured launch of the kernel or hypervisor using TXT and the TPM.

## Why it is Type 2

Type 2: it sits between firmware and the OS, measuring and launching it.

## Security mechanisms

Detected in its build configuration and source:

- fortify
- measured boot
- rollback protection

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/tboot-mirror
./scripts/analysis/run-tool.sh codeql tboot-mirror
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
