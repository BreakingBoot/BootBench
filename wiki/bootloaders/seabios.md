# seabios

*Open-source legacy BIOS implementation, commonly a coreboot payload.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/coreboot/seabios |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 9 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Provides the 16-bit BIOS interrupt interface (int 10h, 13h, 15h) and loads the first sector of a boot device.

## Why it is Type 1

Type 1: it exposes the legacy firmware interface rather than preparing an OS, and chainloads a Type 2 loader from the MBR.

## How it boots

The SoK paper gives a full case study of this bootloader in section 3.2. See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **preinit** -- Runs in 16-bit real mode. Basic CPU and chipset setup, enough to get RAM usable.
2. **init** -- Builds the firmware's data structures -- interrupt vector table, BIOS Data Area, PCI configuration, ACPI and SMBIOS tables.
3. **setup** -- Loads option ROMs from PCI devices and runs them, so peripherals that need their own driver code can install it.
4. **prepboot** -- Finishes hardware initialisation and enumerates bootable devices: floppy, hard disk, CD-ROM, USB, network.
5. **boot** -- Selects a boot device and invokes INT 0x19 to load and enter its boot sector.

### Passing data between stages

SeaBIOS communicates through fixed memory locations and software interrupts rather than tables passed by pointer. The interrupt vector table and the BIOS Data Area at segment 0x40 are at addresses every later stage already knows; the Extended BIOS Data Area sits just below the 640 KB line. Services are reached by interrupt number -- INT 0x10 for video, INT 0x13 for disk, INT 0x15 for the memory map -- and peripherals extend the firmware by contributing option ROMs that hook those vectors. There is no structured handoff record: the contract is the address map itself.

### Handoff

INT 0x19 reads the first sector of the selected device to physical address 0x7C00, checks for the 0xAA55 signature, and jumps there with DL set to the boot drive number. On an MBR disk that sector's 446 bytes of code find the active partition and chain to its Volume Boot Record, which loads the Type 2 bootloader. Nothing is torn down -- the interrupt services stay callable, which is exactly how a loader like GRUB reads the rest of itself off the disk.

## Security mechanisms

Detected in its build configuration and source:

- measured boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/seabios
./scripts/analysis/run-tool.sh codeql seabios
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
