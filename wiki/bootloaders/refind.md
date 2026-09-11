# refind

*Graphical UEFI boot manager.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://git.code.sf.net/p/refind/code |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Scans partitions for boot loaders and kernels and presents a menu.

## Why it is Type 2

Type 2: a UEFI boot manager whose job is choosing and launching an OS.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **loaded by firmware** -- refind_x64.efi is loaded from the ESP as a UEFI application, often in place of the distribution's own loader.
2. **configuration and driver load** -- Reads refind.conf, then loads filesystem drivers from drivers_x64/ so it can read partitions the firmware cannot.
3. **scan** -- Scans volumes for loaders, kernels and OS signatures, and builds a menu automatically from what it finds.
4. **launch** -- Starts the selected image, or a kernel directly if it has an EFI stub.

### Passing data between stages

rEFInd is a boot *manager*: the intelligence is in discovery rather than in loading. Its optional UEFI filesystem drivers extend what the firmware itself can read, which is how it lists kernels on ext4 or Btrfs. Configuration is `refind.conf` plus per-kernel option files (`refind_linux.conf`), and it can consult `/etc/fstab` to work out the correct `root=` argument rather than being told.

### Handoff

A menu selection is a normal UEFI image load: the target gets its own image handle and the same system table. For a Linux kernel built with the EFI stub that target is the kernel itself, so the chain is firmware to rEFInd to kernel with no second loader. For Windows or macOS it is the vendor's own loader. When Secure Boot is in force, rEFInd is normally launched by shim so its own launches can be verified.

## Security mechanisms

Detected in its build configuration and source:

- secure boot
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/refind
./scripts/analysis/run-tool.sh codeql refind
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
