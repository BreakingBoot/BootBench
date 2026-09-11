# linuxboot

*Replaces UEFI DXE with a Linux kernel and userspace.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/linuxboot/linuxboot |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 1 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Keeps vendor PEI for silicon init, then runs Linux as the boot environment.

## Why it is Type 2

Type 2: it is the OS-loading stage layered on vendor Type 1 firmware.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **vendor firmware PEI** -- The platform's existing UEFI firmware runs SEC and PEI to bring up memory.
2. **DXE replacement** -- Most of the DXE volume is removed and replaced with a Linux kernel and initramfs.
3. **Linux start** -- The kernel boots with the drivers the platform needs.
4. **u-root policy** -- The u-root userland runs as init and decides what to boot.
5. **kexec** -- The target OS kernel is loaded and kexec'd.

### Passing data between stages

LinuxBoot is a firmware surgery project: it keeps the vendor's SEC and PEI phases, because memory initialisation is board-specific and often blob-bound, and replaces what comes after with Linux. The consequence for communication is that the UEFI HOB and protocol machinery ends where DXE would have started; from then on the interfaces are the kernel's -- device tree or ACPI, sysfs, standard drivers. Tools in this repository do the splicing on the flash image itself.

### Handoff

The final handoff is a kexec performed by u-root. Because the runtime services a normal UEFI machine would leave behind are largely gone, the OS is booted more like an embedded system than a PC, which is the trade LinuxBoot makes for a much smaller closed-source surface.

## Security mechanisms

Detected in its build configuration and source:

- aslr
- fortify
- rollback protection
- secure boot
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/linuxboot
./scripts/analysis/run-tool.sh codeql linuxboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
