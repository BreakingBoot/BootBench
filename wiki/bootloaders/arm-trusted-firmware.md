# arm-trusted-firmware

*Trusted Firmware-A, the Arm secure-world reference.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/ARM-software/arm-trusted-firmware |
| CVEs attributed | 12 |
| Vulnerability-fixing commits | 60 naming a CVE, 96 keyword-matched |
| CVEs with a linked fix | 2 |

## What it does at boot

BL1/BL2/BL31 bring the SoC up from reset, set up EL3 runtime services, then enter the normal-world bootloader or OS.

## Why it is Type 3

Type 3 in this corpus: it spans reset to OS handoff. Arguably Type 1 in a staged setup where BL33 is U-Boot.

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-1284 | 2 |
| CWE-787 | 1 |
| CWE-191 | 1 |
| CWE-682 | 1 |
| CWE-123 | 1 |
| CWE-120 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- cfi
- encryption
- measured boot
- rollback protection
- secure boot
- signature verification
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Reproducible vulnerabilities

Each of these resolves to a fixing commit and to the parent revision that still contains the bug:

| CVE | Fix | Vulnerable revision |
|---|---|---|
| CVE-2017-15031 | `87d35d933d` | `494d57e8b8` |
| CVE-2017-15031 | `c605ecd1a1` | `a74e3a16b5` |

```bash
git -C oss-bootloaders/type3/arm-trusted-firmware checkout <vulnerable revision>
```

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/arm-trusted-firmware
./scripts/analysis/run-tool.sh codeql arm-trusted-firmware
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
