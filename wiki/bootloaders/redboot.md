# redboot

*RedBoot, the eCos-based ROM monitor.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/hharte/ecos |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 13 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Provides a debug monitor, flash management and network download, then boots an image.

## Why it is Type 3

Type 3: it owns the board from reset.

## Security mechanisms

Detected in its build configuration and source:

- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/redboot
./scripts/analysis/run-tool.sh codeql redboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
