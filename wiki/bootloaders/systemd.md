# systemd

*systemd, whose systemd-boot is a minimal UEFI boot manager.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/systemd/systemd |
| CVEs attributed | 2 |
| Vulnerability-fixing commits | 23 naming a CVE, 312 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Enumerates boot entries from the EFI System Partition and launches the chosen kernel, with no scripting language.

## Why it is Type 2

Type 2: a UEFI application that selects and starts an OS.

## Attack surfaces seen in its CVEs

| Surface | | CVEs |
|---|---|---:|
| `SAS2` | Persistent data source (software) | 1 |

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-522 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- measured boot
- rollback protection
- secure boot
- signature verification
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/systemd
./scripts/analysis/run-tool.sh codeql systemd
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
