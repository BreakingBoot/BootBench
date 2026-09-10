# u-boot

*Das U-Boot, the dominant embedded bootloader.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/u-boot/u-boot |
| CVEs attributed | 70 |
| Vulnerability-fixing commits | 46 naming a CVE, 428 keyword-matched |
| CVEs with a linked fix | 39 |

## What it does at boot

SPL performs DRAM and clock init from reset, then full U-Boot loads a kernel, device tree and initrd, with a command shell and scripting throughout.

## Why it is Type 3

Type 3: SPL plus U-Boot together take the board from reset to a running OS with no separate firmware layer -- one project spans both roles.

## Attack surfaces seen in its CVEs

| Surface | | CVEs |
|---|---|---:|
| `SAS2` | Persistent data source (software) | 20 |
| `SAS1` | Remote access (software) | 6 |
| `HAS2` | External hardware (hardware) | 1 |
| `HAS1` | Invasive hardware (hardware) | 1 |

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-190 | 6 |
| CWE-329 | 2 |
| CWE-122 | 2 |
| CWE-798 | 2 |
| CWE-20 | 2 |
| CWE-120 | 2 |
| CWE-284 | 1 |
| CWE-77 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- fortify
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
| CVE-2017-3225 | `5eb35220b2` | `0683fb7242` |
| CVE-2017-3226 | `5eb35220b2` | `0683fb7242` |
| CVE-2018-18439 | `9cc2323fee` | `e3b4fc9598` |
| CVE-2018-18439 | `67bb984249` | `1a4af5c562` |
| CVE-2018-18439 | `e964df1e2a` | `aac0c29d4b` |
| CVE-2018-18439 | `a156c47e39` | `a85c213f47` |
| CVE-2018-18440 | `e964df1e2a` | `aac0c29d4b` |
| CVE-2018-18440 | `aa3c609e2b` | `4cc8af8037` |
| CVE-2019-13103 | `232e2f4fd9` | `1493b140e4` |
| CVE-2019-13104 | `878269dbe7` | `6e5a79de65` |
| CVE-2019-13105 | `6e5a79de65` | `232e2f4fd9` |
| CVE-2019-13106 | `e205896c53` | `084be43b75` |
| CVE-2019-14192 | `fe7288069d` | `12c2a310e8` |
| CVE-2019-14193 | `fe7288069d` | `12c2a310e8` |
| CVE-2019-14194 | `aa207cf3a6` | `741a8a08eb` |
| … and 24 more | | |

```bash
git -C oss-bootloaders/type3/u-boot checkout <vulnerable revision>
```

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/u-boot
./scripts/analysis/run-tool.sh codeql u-boot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
