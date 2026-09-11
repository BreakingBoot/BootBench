# edk2-platforms

*Board support built on EDK-II.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/tianocore/edk2-platforms |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 4 naming a CVE, 33 keyword-matched |
| CVEs with a linked fix | 2 |

## What it does at boot

Platform-specific PEI/DXE modules for real silicon, consumed with edk2.

## Why it is Type 1

Type 1: the platform half of a UEFI firmware image.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **(no independent boot flow)** -- Supplies the platform, silicon and driver packages that a UEFI firmware image is built from; the SEC/PEI/DXE/BDS flow is EDK II's.

### Passing data between stages

The packages here plug into EDK II's existing mechanisms rather than defining new ones: PEIMs that publish HOBs, DXE drivers that install protocols, and PCDs -- build- or runtime-configurable values -- that a platform sets to select behaviour without editing core code.

### Handoff

There is no handoff of its own. A platform in this tree is compiled together with edk2 into one firmware image, and that image performs the UEFI handoff described under [edk2](bootloaders/edk2).

## Security mechanisms

Detected in its build configuration and source:

- measured boot
- rollback protection
- secure boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Reproducible vulnerabilities

Each of these resolves to a fixing commit and to the parent revision that still contains the bug:

| CVE | Fix | Vulnerable revision |
|---|---|---|
| CVE-2023-45237 | `a5e609dfa9` | `0c80e71261` |
| CVE-2023-45237 | `0c80e71261` | `b40ce006a6` |

```bash
git -C oss-bootloaders/type1/edk2-platforms checkout <vulnerable revision>
```

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/edk2-platforms
./scripts/analysis/run-tool.sh codeql edk2-platforms
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
