# kexec-tools

*Userspace tooling to boot a new kernel from a running one.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/horms/kexec-tools |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 12 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Loads a kernel image into memory and transfers control without firmware re-init.

## Why it is Type 2

Type 2: an OS-loading stage that assumes a fully initialised machine.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/kexec-tools
./scripts/analysis/run-tool.sh codeql kexec-tools
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
