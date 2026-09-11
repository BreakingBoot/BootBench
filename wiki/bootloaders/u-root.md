# u-root

*Go userspace and bootloader for LinuxBoot.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/u-root/u-root |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 1 naming a CVE, 14 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Runs as an initramfs inside a Linux kernel embedded in firmware, then kexecs the target kernel.

## Why it is Type 2

Type 2: the OS-facing half of a LinuxBoot image; the firmware beneath it is Type 1.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **initramfs start** -- The Linux kernel starts u-root's Go userland as PID 1 from an initramfs.
2. **init and shell** -- Sets up /proc, /sys and /dev, then runs the u-root shell or a specified uinit.
3. **boot policy** -- Commands such as `boot`, `fbnetboot` or `localboot` find boot targets on disk or over the network.
4. **kexec** -- The selected kernel and initrd are loaded and kexec'd.

### Passing data between stages

u-root is a userland, so its interfaces are files and syscalls rather than tables: it reads existing configurations (GRUB, syslinux, BLS entries) from mounted filesystems, gets network configuration over DHCP, and can verify what it found using TPM measurements or signatures before acting on it. Because the boot policy is a Go program, an operator can replace it entirely, which is the LinuxBoot argument -- driver and policy code moves out of firmware and into a kernel and userland that can be updated and audited normally.

### Handoff

The handoff is kexec into the target kernel. u-root's own kexec implementation builds the boot parameters and calls `kexec_file_load` where available, so signature verification can be done by the kernel rather than in userspace.

## Security mechanisms

Detected in its build configuration and source:

- cfi
- fortify
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/u-root
./scripts/analysis/run-tool.sh codeql u-root
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
