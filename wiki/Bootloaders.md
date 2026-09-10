# Bootloaders

Every project in the corpus, grouped by type. Each page explains what the bootloader does at boot, why it is classified as it is, the attack surfaces its CVEs touch, and what it defends itself with.

## Firmware bootloader (`type1`)

| Bootloader | What it is |
|---|---|
| [LakeBIOS](bootloaders/LakeBIOS) | Minimal experimental x86 BIOS implementation. |
| [coreboot](bootloaders/coreboot) | Open-source replacement for proprietary x86 firmware. |
| [edk2](bootloaders/edk2) | TianoCore's reference implementation of UEFI. |
| [edk2-platforms](bootloaders/edk2-platforms) | Board support built on EDK-II. |
| [firmware-open](bootloaders/firmware-open) | System76's open firmware distribution. |
| [hostboot](bootloaders/hostboot) | IBM OpenPOWER host firmware. |
| [lbmk](bootloaders/lbmk) | Libreboot's build system, packaging coreboot with free payloads. |
| [mu_basecore](bootloaders/mu_basecore) | Microsoft's Project Mu fork of EDK-II. |
| [openbios](bootloaders/openbios) | Free IEEE 1275 Open Firmware implementation. |
| [openfirmware](bootloaders/openfirmware) | Mitch Bradley's original IEEE 1275 Open Firmware. |
| [opensbi](bootloaders/opensbi) | RISC-V Supervisor Binary Interface reference implementation. |
| [oreboot](bootloaders/oreboot) | coreboot rewritten in Rust, with no C. |
| [seabios](bootloaders/seabios) | Open-source legacy BIOS implementation, commonly a coreboot payload. |
| [slimbootloader](bootloaders/slimbootloader) | Intel's lightweight, fast-boot firmware for IoT and embedded x86. |

## OS bootloader (`type2`)

| Bootloader | What it is |
|---|---|
| [CloverBootloader](bootloaders/CloverBootloader) | Clover, an earlier macOS-focused UEFI bootloader. |
| [MiniVisorPkg](bootloaders/MiniVisorPkg) | Minimal research hypervisor loadable from UEFI. |
| [OpenCorePkg](bootloaders/OpenCorePkg) | OpenCore, a UEFI bootloader for running macOS on unsupported hardware. |
| [aboot](bootloaders/aboot) | Android bootloader (the historical Alpha aboot in this corpus). |
| [bootboot](bootloaders/bootboot) | Multi-architecture boot protocol and reference loaders. |
| [bootloader](bootloaders/bootloader) | rust-osdev/bootloader, a Rust x86_64 kernel loader. |
| [chameleon](bootloaders/chameleon) | Legacy Darwin/x86 boot loader. |
| [depthcharge](bootloaders/depthcharge) | ChromeOS bootloader, a coreboot payload. |
| [easyboot](bootloaders/easyboot) | Multi-kernel boot manager built on the BOOTBOOT protocol. |
| [grub](bootloaders/grub) | GNU GRUB 2, the dominant Linux boot loader. |
| [ipxe](bootloaders/ipxe) | Open-source network boot firmware. |
| [kexec-tools](bootloaders/kexec-tools) | Userspace tooling to boot a new kernel from a running one. |
| [limine](bootloaders/limine) | Modern multi-protocol bootloader for x86 and aarch64. |
| [linuxboot](bootloaders/linuxboot) | Replaces UEFI DXE with a Linux kernel and userspace. |
| [lk](bootloaders/lk) | Little Kernel, a small embedded OS used as a bootloader. |
| [lk2nd](bootloaders/lk2nd) | Second-stage LK bootloader for msm8916 mainline Linux. |
| [open-iscsi](bootloaders/open-iscsi) | Linux iSCSI initiator, used for network root and boot. |
| [petitboot](bootloaders/petitboot) | kexec-based bootloader for OpenPOWER. |
| [quibble](bootloaders/quibble) | Open-source Windows boot loader replacement. |
| [refind](bootloaders/refind) | Graphical UEFI boot manager. |
| [shim](bootloaders/shim) | Signed first-stage UEFI loader that extends Secure Boot to distro keys. |
| [skiboot](bootloaders/skiboot) | OPAL firmware for OpenPOWER. |
| [syslinux](bootloaders/syslinux) | SYSLINUX family: SYSLINUX, ISOLINUX, PXELINUX, EXTLINUX. |
| [systemd](bootloaders/systemd) | systemd, whose systemd-boot is a minimal UEFI boot manager. |
| [tboot-mirror](bootloaders/tboot-mirror) | Trusted Boot, a pre-kernel module for Intel TXT measured launch. |
| [tosaithe](bootloaders/tosaithe) | Minimal UEFI boot menu and Stivale2 loader. |
| [u-root](bootloaders/u-root) | Go userspace and bootloader for LinuxBoot. |
| [x86-bootloader](bootloaders/x86-bootloader) | Teaching-scale x86 bootloader. |

## Monolithic bootloader (`type3`)

| Bootloader | What it is |
|---|---|
| [Adafruit_nRF52_Bootloader](bootloaders/Adafruit_nRF52_Bootloader) | UF2 and DFU bootloader for nRF52 boards. |
| [IMBootloader](bootloaders/IMBootloader) | IMProject bootloader for STM32. |
| [STM32duino-bootloader](bootloaders/STM32duino-bootloader) | USB DFU bootloader for STM32F1 boards. |
| [arduino-variometer](bootloaders/arduino-variometer) | Arduino variometer project including its bootloader. |
| [arm-trusted-firmware](bootloaders/arm-trusted-firmware) | Trusted Firmware-A, the Arm secure-world reference. |
| [barebox](bootloaders/barebox) | U-Boot alternative with a Linux-like driver model. |
| [firmware](bootloaders/firmware) | Meshtastic device firmware. |
| [harmony](bootloaders/harmony) | Microchip Harmony bootloader framework. |
| [katapult](bootloaders/katapult) | CAN, USB and UART bootloader for MCUs, common on 3D printer boards. |
| [mbed-bootloader](bootloaders/mbed-bootloader) | Mbed OS bootloader with firmware update support. |
| [mcuboot](bootloaders/mcuboot) | Secure bootloader for 32-bit microcontrollers. |
| [openblt](bootloaders/openblt) | Open-source bootloader for automotive and embedded MCUs. |
| [optiboot](bootloaders/optiboot) | The small AVR bootloader shipped on most Arduino boards. |
| [redboot](bootloaders/redboot) | RedBoot, the eCos-based ROM monitor. |
| [rustBoot](bootloaders/rustBoot) | Secure bootloader for MCUs written in Rust. |
| [stm32-mw-openbl](bootloaders/stm32-mw-openbl) | STMicroelectronics OpenBootLoader middleware. |
| [tock-bootloader](bootloaders/tock-bootloader) | Bootloader for the Tock embedded OS. |
| [trusted-firmware-m](bootloaders/trusted-firmware-m) | Trusted Firmware-M, the Armv8-M secure runtime. |
| [u-boot](bootloaders/u-boot) | Das U-Boot, the dominant embedded bootloader. |
| [wolfBoot](bootloaders/wolfBoot) | Portable secure bootloader from wolfSSL. |
