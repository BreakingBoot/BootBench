# barebox

*U-Boot alternative with a Linux-like driver model.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/barebox/barebox |
| CVEs attributed | 13 |
| Vulnerability-fixing commits | 6 naming a CVE, 265 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Initialises the board from reset and boots a kernel, with a shell and a filesystem-like device model.

## Why it is Type 3

Type 3: hardware bring-up and OS launch in one image.

## Attack surfaces seen in its CVEs

| Surface | | CVEs |
|---|---|---:|
| `SAS1` | Remote access (software) | 4 |
| `SAS2` | Persistent data source (software) | 3 |
| `HAS2` | External hardware (hardware) | 2 |

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-190 | 3 |
| CWE-125 | 2 |
| CWE-345 | 1 |
| CWE-835 | 1 |
| CWE-346 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- encryption
- fortify
- measured boot
- rollback protection
- secure boot
- signature verification
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/barebox
./scripts/analysis/run-tool.sh codeql barebox
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
