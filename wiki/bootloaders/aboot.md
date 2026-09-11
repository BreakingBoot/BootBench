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

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **SRM console** -- Alpha's SRM firmware initialises the machine and reads the bootstrap blocks from the boot device.
2. **bootstrap loader** -- The bootblock loads aboot itself from the reserved area at the start of the disk.
3. **filesystem access** -- aboot reads ext2, ISO 9660 or UFS directly to find the kernel.
4. **kernel load** -- Loads the kernel, resolves arguments from /etc/aboot.conf, and starts it.

### Passing data between stages

aboot sits on SRM's callback interface: the firmware stays available for console and disk access, so aboot does not need its own drivers for the boot path. Its own configuration is `/etc/aboot.conf`, read from the target filesystem, where numbered entries map a short selection made at the SRM prompt onto a full kernel path and command line. This is the Alpha equivalent of the arrangement the paper describes for BIOS-era loaders -- firmware services remain callable across the boundary.

### Handoff

The kernel is entered with its command line and, where used, an initial ramdisk. It is a historical loader, included in the corpus as an example of a non-x86, non-ARM boot path built on a firmware callback interface rather than on tables.

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
