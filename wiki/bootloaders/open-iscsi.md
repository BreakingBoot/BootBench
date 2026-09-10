# open-iscsi

*Linux iSCSI initiator, used for network root and boot.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/open-iscsi/open-iscsi |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 6 naming a CVE, 32 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Establishes iSCSI sessions so a remote volume can serve as the boot disk.

## Why it is Type 2

Type 2 by association: it is boot-path infrastructure for network boot rather than a bootloader that transfers control to a kernel. The weakest fit in the corpus.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/open-iscsi
./scripts/analysis/run-tool.sh codeql open-iscsi
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
