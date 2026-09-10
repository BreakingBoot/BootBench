# MiniVisorPkg

*Minimal research hypervisor loadable from UEFI.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/tandasat/MiniVisorPkg |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Installs a thin hypervisor before the OS boots.

## Why it is Type 2

Type 2: a UEFI-loaded stage that runs before and hands off to an OS.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/MiniVisorPkg
./scripts/analysis/run-tool.sh codeql MiniVisorPkg
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
