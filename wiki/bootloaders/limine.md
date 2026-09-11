# limine

*Modern multi-protocol bootloader for x86 and aarch64.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/limine-bootloader/limine |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 10 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Supports its own protocol plus Linux, Multiboot and chainloading, from BIOS or UEFI.

## Why it is Type 2

Type 2: boots from an initialised platform into an OS kernel.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **stage1** -- On BIOS, a 512-byte MBR/VBR stage that loads stage2. On UEFI, the firmware loads BOOTX64.EFI directly and this stage does not exist.
2. **stage2** -- Decompresses and enters the main bootloader image.
3. **common** -- The bootloader proper: filesystem drivers, the config parser, the menu and the terminal.
4. **protocol handler** -- Loads the kernel according to the protocol it asks for -- Limine, Multiboot1/2, Linux or chainload.

### Passing data between stages

Configuration is a single `limine.conf` on the boot partition. What distinguishes Limine is the shape of the handoff rather than the configuration: instead of one information structure, the kernel embeds a list of *request* structures, each tagged with a magic number, and the bootloader scans the loaded image for them and fills in the responses it recognises. A kernel asks only for what it needs -- memory map, framebuffer, higher-half direct map, SMP -- and the two sides stay compatible as the protocol grows.

### Handoff

The kernel is entered in a defined state: 64-bit long mode already on, its own page tables installed with the higher-half direct map in place, a stack allocated, and the response structures filled in. Under UEFI, `ExitBootServices()` has already been called. Multiboot and Linux kernels are booted with their own protocols instead.

## Security mechanisms

Detected in its build configuration and source:

- secure boot

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/limine
./scripts/analysis/run-tool.sh codeql limine
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
