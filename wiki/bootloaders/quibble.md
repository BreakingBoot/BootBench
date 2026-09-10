# quibble

*Open-source Windows boot loader replacement.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/maharmstone/quibble |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Loads the Windows kernel from a filesystem GRUB can reach.

## Why it is Type 2

Type 2: it prepares and launches an OS.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/quibble
./scripts/analysis/run-tool.sh codeql quibble
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
