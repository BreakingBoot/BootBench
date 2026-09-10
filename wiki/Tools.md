# Tools

The analysis tools BootBench collects, with a page each covering how the tool works, what it applies to, and a walkthrough.

| Tool | Applies to | Status |
|---|---|---|
| [angr](tools/angr) | Any compiled bootloader: ELF (U-Boot sandbox, kexec) or PE (shim, GRUB, any DXE module). R | `runnable` |
| [arbiter](tools/arbiter) | Compiled bootloader binaries, x86/x86-64. Needs a template naming the sinks. | `runnable` |
| [ASPFuzz](tools/ASPFuzz) | The AMD Secure Processor on-chip bootloader only. | `needs-hardware` |
| [binwalk](tools/binwalk) | Any firmware image or flash dump, UEFI or embedded. | `runnable` |
| [BootStomp](tools/BootStomp) | Android bootloaders only: Qualcomm LK (type2/lk), Huawei fastboot, Nexus hboot, Xperia LK. | `runnable` |
| [chipsec](tools/chipsec) | UEFI firmware images offline. On-target platform checks need the live machine. | `runnable` |
| [codeql](tools/codeql) | Any bootloader that builds. 7 of 16 recipes in build_commands.json are verified end to end | `runnable` |
| [efi_fuzz](tools/efi_fuzz) | UEFI DXE and SMM drivers from EDK-II or an OEM image. Ships three worked examples. | `runnable` |
| [emba](tools/emba) | Whole firmware images, UEFI or Linux-based embedded. Broad rather than bootloader-specific | `runnable` |
| [emmutaler](tools/emmutaler) | Apple iBoot only. | `needs-hardware` |
| [FACT_core](tools/FACT_core) | Whole firmware images of any kind. | `manual` |
| [fiano](tools/fiano) | UEFI firmware images, same as UEFITool. Go-based, good for scripting. | `runnable` |
| [firmadyne](tools/firmadyne) | Linux-based router and IoT firmware images. Not bootloaders. | `manual` |
| [FirmAE](tools/FirmAE) | Linux-based router and IoT firmware images. Not bootloaders. | `manual` |
| [fwhunt-scan](tools/fwhunt-scan) | Individual UEFI modules (PE32+) from EDK-II, Project Mu or an OEM image. | `runnable` |
| [fwupd](tools/fwupd) | Any firmware blob, offline. Identifies the container format and hashes it as Secure Boot w | `runnable` |
| [karonte](tools/karonte) | Firmware binaries with multiple communicating components. Ships configs for Qualcomm LK (t | `runnable` |
| [MEAnalyzer](tools/MEAnalyzer) | Intel ME/CSME/TXE regions, which sit beside the bootloader in the same flash part. Not pre | `runnable` |
| [pesign](tools/pesign) | Signed PE bootloaders: shim, GRUB's EFI build, systemd-boot, any signed DXE module. | `runnable` |
| [top4grep](tools/top4grep) | Not a bootloader tool: searches conference proceedings. | `runnable` |
| [tsffs](tools/tsffs) | Anything Simics can simulate, including UEFI and embedded bootloaders. | `needs-license` |
| [uefi-firmware-parser](tools/uefi-firmware-parser) | UEFI firmware images plus Intel flash descriptors. | `runnable` |
| [uefi_retool](tools/uefi_retool) | UEFI firmware images, for module extraction only. Protocol recovery needs IDA Pro. | `runnable` |
| [UEFITool](tools/UEFITool) | UEFI firmware images: OVMF from edk2, Project Mu builds, OEM flash dumps. | `runnable` |
