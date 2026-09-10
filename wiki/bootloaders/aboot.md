# aboot

*Android bootloader (the historical Alpha aboot in this corpus).*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/mattst88/aboot |
| CVEs attributed | 13 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Loads and verifies an Android boot image.

## Why it is Type 2

Type 2: an OS-loading stage.

## Attack surfaces seen in its CVEs

| Surface | | CVEs |
|---|---|---:|
| `SAS4` | Boot-time features (software) | 2 |
| `SAS2` | Persistent data source (software) | 2 |
| `HAS2` | External hardware (hardware) | 1 |

## Security mechanisms

Detected in its build configuration and source:

- fortify

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/aboot
./scripts/analysis/run-tool.sh codeql aboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
