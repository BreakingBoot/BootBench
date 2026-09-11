# slimbootloader

*Intel's lightweight, fast-boot firmware for IoT and embedded x86.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/slimbootloader/slimbootloader |
| CVEs attributed | 5 |
| Vulnerability-fixing commits | 0 naming a CVE, 21 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Stage1A/1B/2 silicon init via FSP, then launches an OS loader or payload.

## Why it is Type 1

Type 1: FSP-based silicon init with a payload handoff, the same structure as coreboot.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **Stage1A** -- Runs from reset out of flash. Calls the Intel FSP `TempRamInit` entry to get cache-as-RAM, then loads Stage1B.
2. **Stage1B** -- Calls FSP `FspMemoryInit` to bring up DRAM, verifies and loads Stage2, and migrates state out of temporary memory.
3. **Stage2** -- Calls FSP `FspSiliconInit`, enumerates PCI, builds ACPI and SMBIOS tables, and prepares the payload environment.
4. **Payload** -- Loads a payload -- OsLoader, a UEFI payload, or a custom one -- from the boot partition.

### Passing data between stages

Slim Bootloader inherits EDK II's HOB mechanism: FSP returns its results as HOBs, and each stage adds its own before passing the list on. Board configuration is kept out of code in signed Configuration Data blobs (CFGDATA) stored in flash, which a later stage reads rather than recompiling for. A stage transition on this design is a verified load: each stage measures and checks the next against keys in the key store before jumping.

### Handoff

Stage2 hands the payload a HOB list describing memory, the serial port, the framebuffer, the performance log and the boot device. The stock OsLoader payload then locates a kernel and boots it directly; a UEFI payload instead rebuilds full UEFI services on top of what it was given, in the same way a UEFI payload does over coreboot.

## Attack surfaces seen in its CVEs

| Surface | | CVEs |
|---|---|---:|
| `SAS3` | Post-boot features (software) | 1 |

## Most common weaknesses

| CWE | CVEs |
|---|---:|
| CWE-190 | 2 |
| CWE-287 | 1 |
| CWE-693 | 1 |
| CWE-787 | 1 |

## Security mechanisms

Detected in its build configuration and source:

- cfi
- measured boot
- rollback protection
- secure boot
- signature verification

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/slimbootloader
./scripts/analysis/run-tool.sh codeql slimbootloader
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
