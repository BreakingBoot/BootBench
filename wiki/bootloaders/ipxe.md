# ipxe

*Open-source network boot firmware.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/ipxe/ipxe |
| CVEs attributed | 3 |
| Vulnerability-fixing commits | 0 naming a CVE, 54 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Provides PXE and its own scripting, fetching kernels over HTTP, iSCSI or Infiniband and booting them.

## Why it is Type 2

Type 2: it runs as an option ROM or UEFI application on an initialised machine and loads an OS over the network.

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-284 | 1 |
| CWE-347 | 1 |
| CWE-669 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- cfi
- encryption
- measured boot
- secure boot
- signature verification
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/ipxe
./scripts/analysis/run-tool.sh codeql ipxe
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
