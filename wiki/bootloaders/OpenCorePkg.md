# OpenCorePkg

*OpenCore, a UEFI bootloader for running macOS on unsupported hardware.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/acidanthera/OpenCorePkg |
| CVEs attributed | 1 |
| Vulnerability-fixing commits | 1 naming a CVE, 26 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Injects ACPI, kext and SMBIOS patches, then boots macOS, Windows or Linux.

## Why it is Type 2

Type 2: a UEFI application that prepares and launches an OS.

## Attack surfaces seen in its CVEs

| Surface | | CVEs |
|---|---|---:|
| `SAS1` | Remote access (software) | 1 |

## Security mechanisms

Detected in its build configuration and source:

- cfi
- secure boot
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/OpenCorePkg
./scripts/analysis/run-tool.sh codeql OpenCorePkg
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
