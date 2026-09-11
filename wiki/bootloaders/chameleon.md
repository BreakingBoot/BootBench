# chameleon

*Legacy Darwin/x86 boot loader.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/rescbr/chameleon |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 7 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

BIOS-era loader for booting macOS on generic hardware.

## Why it is Type 2

Type 2: it loads an OS from an initialised BIOS machine.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **boot0** -- MBR code that finds the active partition and loads boot1.
2. **boot1** -- Partition boot sector code that locates the boot file in the filesystem.
3. **boot2** -- The bootloader proper: reads configuration, patches tables, presents a device picker.
4. **kernel load** -- Loads the XNU kernel and mkext/kext caches, applies patches, and enters the kernel.

### Passing data between stages

Chameleon descends from Apple's open-source boot-132 and works entirely in the legacy BIOS world, so its stage boundaries are the classic sector-size ones and its services come from BIOS interrupts. Configuration is `org.chameleon.Boot.plist`, and injection is done by building the ACPI tables, SMBIOS and device properties in memory before XNU is started. It is effectively superseded by Clover and OpenCore, which is why it appears here mainly as the earlier generation of the same idea.

### Handoff

The XNU kernel is entered directly with a boot-args structure describing memory, the framebuffer and the kernel command line, together with the device tree Chameleon constructed. Unlike the UEFI-era loaders there is no `boot.efi` in the chain.

## Security mechanisms

Detected in its build configuration and source:

- encryption
- fortify

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/chameleon
./scripts/analysis/run-tool.sh codeql chameleon
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
