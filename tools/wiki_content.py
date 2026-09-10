"""Curated prose for the wiki: what each bootloader is, and why it is its type.

The structural parts of a wiki page -- CVE counts, defenses, commit history --
are generated from the datasets. What cannot be generated is the explanation:
what a bootloader actually does at boot, and why that places it in Type 1, 2
or 3. That judgement lives here, one entry per corpus project.

Each entry is (summary, boot_role, type_rationale). `type_rationale` should
answer the question the taxonomy turns on: where does it start, and what does
it hand off to?
"""

from __future__ import annotations

# Bootloaders whose classification is genuinely arguable are marked in the
# rationale rather than presented as settled.
BOOTLOADERS: dict[str, tuple[str, str, str]] = {
    # ---- Type 1: firmware bootloaders -------------------------------------
    "coreboot": (
        "Open-source replacement for proprietary x86 firmware.",
        "Runs from the reset vector, performs raw silicon and DRAM init, then hands "
        "control to a payload (SeaBIOS, GRUB, Linux, Tianocore) that does the OS-facing work.",
        "Type 1: it starts from hardware with nothing initialised and deliberately does "
        "not load an OS itself -- the payload split is the defining Type 1 handoff.",
    ),
    "edk2": (
        "TianoCore's reference implementation of UEFI.",
        "Runs SEC, PEI, DXE and BDS phases, brings up the platform, publishes Boot "
        "Services and Runtime Services, then selects a boot application via BootOrder.",
        "Type 1: it presents the hardware-agnostic UEFI interface that later stages "
        "consume, and remains OS-agnostic -- it loads a Type 2 loader, not a kernel.",
    ),
    "seabios": (
        "Open-source legacy BIOS implementation, commonly a coreboot payload.",
        "Provides the 16-bit BIOS interrupt interface (int 10h, 13h, 15h) and loads the "
        "first sector of a boot device.",
        "Type 1: it exposes the legacy firmware interface rather than preparing an OS, "
        "and chainloads a Type 2 loader from the MBR.",
    ),
    "slimbootloader": (
        "Intel's lightweight, fast-boot firmware for IoT and embedded x86.",
        "Stage1A/1B/2 silicon init via FSP, then launches an OS loader or payload.",
        "Type 1: FSP-based silicon init with a payload handoff, the same structure as "
        "coreboot.",
    ),
    "openbios": (
        "Free IEEE 1275 Open Firmware implementation.",
        "Provides a Forth interpreter and device tree, then boots a client program.",
        "Type 1: it is the firmware interface itself, exposing device abstractions "
        "rather than preparing a specific OS.",
    ),
    "openfirmware": (
        "Mitch Bradley's original IEEE 1275 Open Firmware.",
        "Forth-based firmware providing device discovery, a device tree and a client "
        "interface for the OS loader.",
        "Type 1: the canonical hardware-agnostic firmware interface.",
    ),
    "hostboot": (
        "IBM OpenPOWER host firmware.",
        "Initialises POWER processors and memory from the service processor handoff, "
        "then loads skiboot.",
        "Type 1: bare-hardware bring-up that hands off to a separate OS-facing stage.",
    ),
    "lbmk": (
        "Libreboot's build system, packaging coreboot with free payloads.",
        "Produces coreboot images with GRUB or SeaBIOS payloads for supported machines.",
        "Type 1: a distribution of Type 1 firmware; the payload it bundles is Type 2.",
    ),
    "firmware-open": (
        "System76's open firmware distribution.",
        "coreboot plus EDK-II payload and System76 EC firmware for their laptops.",
        "Type 1: vendor packaging of Type 1 firmware.",
    ),
    "LakeBIOS": (
        "Minimal experimental x86 BIOS implementation.",
        "Brings up a QEMU-class machine and provides a minimal BIOS interface.",
        "Type 1: firmware-level bring-up from reset.",
    ),
    "oreboot": (
        "coreboot rewritten in Rust, with no C.",
        "Performs silicon init and hands to a payload, targeting RISC-V and ARM as well as x86.",
        "Type 1: same role and payload handoff as coreboot, different language.",
    ),
    "mu_basecore": (
        "Microsoft's Project Mu fork of EDK-II.",
        "Supplies the core UEFI packages that Mu platform repositories build against; "
        "ships on Surface devices and Hyper-V.",
        "Type 1: a UEFI implementation. Note it is a library repository, not a "
        "standalone buildable platform.",
    ),
    "edk2-platforms": (
        "Board support built on EDK-II.",
        "Platform-specific PEI/DXE modules for real silicon, consumed with edk2.",
        "Type 1: the platform half of a UEFI firmware image.",
    ),
    "opensbi": (
        "RISC-V Supervisor Binary Interface reference implementation.",
        "Runs in M-mode, sets up the machine, provides the SBI ABI, then enters S-mode "
        "at the next stage.",
        "Type 1: it is the privileged firmware layer presenting a stable interface to "
        "whatever boots next -- the RISC-V analogue of UEFI's role.",
    ),

    # ---- Type 2: OS bootloaders -------------------------------------------
    "grub": (
        "GNU GRUB 2, the dominant Linux boot loader.",
        "Reads grub.cfg, offers a menu and a scripting shell, loads a kernel and initrd "
        "from a filesystem, and boots it or chainloads another loader.",
        "Type 2: it starts from an already-initialised machine, is driven entirely by "
        "on-disk configuration, and its whole purpose is preparing an OS.",
    ),
    "shim": (
        "Signed first-stage UEFI loader that extends Secure Boot to distro keys.",
        "Verifies and loads the next stage (usually GRUB) against its own key database "
        "and SBAT revocation levels.",
        "Type 2: it runs on top of UEFI firmware and exists solely to get an OS loader "
        "trusted and running.",
    ),
    "systemd": (
        "systemd, whose systemd-boot is a minimal UEFI boot manager.",
        "Enumerates boot entries from the EFI System Partition and launches the chosen "
        "kernel, with no scripting language.",
        "Type 2: a UEFI application that selects and starts an OS.",
    ),
    "limine": (
        "Modern multi-protocol bootloader for x86 and aarch64.",
        "Supports its own protocol plus Linux, Multiboot and chainloading, from BIOS or UEFI.",
        "Type 2: boots from an initialised platform into an OS kernel.",
    ),
    "refind": (
        "Graphical UEFI boot manager.",
        "Scans partitions for boot loaders and kernels and presents a menu.",
        "Type 2: a UEFI boot manager whose job is choosing and launching an OS.",
    ),
    "ipxe": (
        "Open-source network boot firmware.",
        "Provides PXE and its own scripting, fetching kernels over HTTP, iSCSI or "
        "Infiniband and booting them.",
        "Type 2: it runs as an option ROM or UEFI application on an initialised machine "
        "and loads an OS over the network.",
    ),
    "depthcharge": (
        "ChromeOS bootloader, a coreboot payload.",
        "Implements Chrome OS verified boot, selects a kernel partition and boots it.",
        "Type 2: it is the payload that coreboot (Type 1) hands off to, and it prepares "
        "an OS.",
    ),
    "lk": (
        "Little Kernel, a small embedded OS used as a bootloader.",
        "Used by Qualcomm as the Android aboot bootloader: initialises minimal hardware, "
        "verifies and boots the Android boot image.",
        "Type 2 in this corpus: it runs after the SoC's primary bootloader has brought "
        "the platform up, and loads an OS. Arguably Type 3 on platforms where it is the "
        "only stage.",
    ),
    "lk2nd": (
        "Second-stage LK bootloader for msm8916 mainline Linux.",
        "Loads from the stock aboot and boots mainline Linux with a proper device tree.",
        "Type 2: explicitly a second stage that prepares an OS.",
    ),
    "skiboot": (
        "OPAL firmware for OpenPOWER.",
        "Loaded by hostboot, provides OPAL runtime services and boots a Linux kernel "
        "via petitboot.",
        "Type 2: it starts from hostboot's initialised state and prepares an OS.",
    ),
    "petitboot": (
        "kexec-based bootloader for OpenPOWER.",
        "Runs in a small Linux environment, discovers boot options and kexecs the target "
        "kernel.",
        "Type 2: it runs on an initialised platform and its only job is launching an OS.",
    ),
    "kexec-tools": (
        "Userspace tooling to boot a new kernel from a running one.",
        "Loads a kernel image into memory and transfers control without firmware re-init.",
        "Type 2: an OS-loading stage that assumes a fully initialised machine.",
    ),
    "u-root": (
        "Go userspace and bootloader for LinuxBoot.",
        "Runs as an initramfs inside a Linux kernel embedded in firmware, then kexecs "
        "the target kernel.",
        "Type 2: the OS-facing half of a LinuxBoot image; the firmware beneath it is Type 1.",
    ),
    "linuxboot": (
        "Replaces UEFI DXE with a Linux kernel and userspace.",
        "Keeps vendor PEI for silicon init, then runs Linux as the boot environment.",
        "Type 2: it is the OS-loading stage layered on vendor Type 1 firmware.",
    ),
    "syslinux": (
        "SYSLINUX family: SYSLINUX, ISOLINUX, PXELINUX, EXTLINUX.",
        "Boots Linux from FAT, ISO9660, network or ext filesystems, driven by a config file.",
        "Type 2: configuration-driven OS loading from an initialised machine.",
    ),
    "bootboot": (
        "Multi-architecture boot protocol and reference loaders.",
        "Provides a uniform machine state to the kernel across BIOS, UEFI and RPi.",
        "Type 2: implements a protocol for handing off to an OS kernel.",
    ),
    "OpenCorePkg": (
        "OpenCore, a UEFI bootloader for running macOS on unsupported hardware.",
        "Injects ACPI, kext and SMBIOS patches, then boots macOS, Windows or Linux.",
        "Type 2: a UEFI application that prepares and launches an OS.",
    ),
    "CloverBootloader": (
        "Clover, an earlier macOS-focused UEFI bootloader.",
        "Similar role to OpenCore, with its own patching model.",
        "Type 2: a UEFI application that launches an OS.",
    ),
    "chameleon": (
        "Legacy Darwin/x86 boot loader.",
        "BIOS-era loader for booting macOS on generic hardware.",
        "Type 2: it loads an OS from an initialised BIOS machine.",
    ),
    "tboot-mirror": (
        "Trusted Boot, a pre-kernel module for Intel TXT measured launch.",
        "Performs a measured launch of the kernel or hypervisor using TXT and the TPM.",
        "Type 2: it sits between firmware and the OS, measuring and launching it.",
    ),
    "aboot": (
        "Android bootloader (the historical Alpha aboot in this corpus).",
        "Loads and verifies an Android boot image.",
        "Type 2: an OS-loading stage.",
    ),
    "quibble": (
        "Open-source Windows boot loader replacement.",
        "Loads the Windows kernel from a filesystem GRUB can reach.",
        "Type 2: it prepares and launches an OS.",
    ),
    "easyboot": (
        "Multi-kernel boot manager built on the BOOTBOOT protocol.",
        "Presents a menu and boots kernels in several formats.",
        "Type 2: OS selection and launch.",
    ),
    "tosaithe": (
        "Minimal UEFI boot menu and Stivale2 loader.",
        "Boots hobby-OS kernels from UEFI.",
        "Type 2: a UEFI application that loads a kernel.",
    ),
    "x86-bootloader": (
        "Teaching-scale x86 bootloader.",
        "A minimal MBR loader demonstrating the real-mode to protected-mode transition.",
        "Type 2: it starts after BIOS and loads a kernel.",
    ),
    "bootloader": (
        "rust-osdev/bootloader, a Rust x86_64 kernel loader.",
        "Loads a Rust kernel from BIOS or UEFI and sets up paging before handoff.",
        "Type 2: it starts from an initialised platform and prepares a kernel.",
    ),
    "MiniVisorPkg": (
        "Minimal research hypervisor loadable from UEFI.",
        "Installs a thin hypervisor before the OS boots.",
        "Type 2: a UEFI-loaded stage that runs before and hands off to an OS.",
    ),
    "open-iscsi": (
        "Linux iSCSI initiator, used for network root and boot.",
        "Establishes iSCSI sessions so a remote volume can serve as the boot disk.",
        "Type 2 by association: it is boot-path infrastructure for network boot rather "
        "than a bootloader that transfers control to a kernel. The weakest fit in the corpus.",
    ),

    # ---- Type 3: monolithic bootloaders -----------------------------------
    "u-boot": (
        "Das U-Boot, the dominant embedded bootloader.",
        "SPL performs DRAM and clock init from reset, then full U-Boot loads a kernel, "
        "device tree and initrd, with a command shell and scripting throughout.",
        "Type 3: SPL plus U-Boot together take the board from reset to a running OS with "
        "no separate firmware layer -- one project spans both roles.",
    ),
    "barebox": (
        "U-Boot alternative with a Linux-like driver model.",
        "Initialises the board from reset and boots a kernel, with a shell and a "
        "filesystem-like device model.",
        "Type 3: hardware bring-up and OS launch in one image.",
    ),
    "mcuboot": (
        "Secure bootloader for 32-bit microcontrollers.",
        "Validates image signatures, manages primary/secondary slots, handles rollback "
        "and swap, then jumps to the application.",
        "Type 3: it runs from reset on the MCU and jumps straight into the application "
        "-- there is no OS-loader stage to hand off to.",
    ),
    "arm-trusted-firmware": (
        "Trusted Firmware-A, the Arm secure-world reference.",
        "BL1/BL2/BL31 bring the SoC up from reset, set up EL3 runtime services, then "
        "enter the normal-world bootloader or OS.",
        "Type 3 in this corpus: it spans reset to OS handoff. Arguably Type 1 in a "
        "staged setup where BL33 is U-Boot.",
    ),
    "trusted-firmware-m": (
        "Trusted Firmware-M, the Armv8-M secure runtime.",
        "Secure boot (often MCUboot-based BL2) plus the secure processing environment "
        "the non-secure application calls into.",
        "Type 3: reset to application on a microcontroller.",
    ),
    "wolfBoot": (
        "Portable secure bootloader from wolfSSL.",
        "Verifies firmware signatures with wolfCrypt, supports rollback protection and "
        "encrypted updates, then boots the application.",
        "Type 3: MCU-class reset-to-application boot.",
    ),
    "rustBoot": (
        "Secure bootloader for MCUs written in Rust.",
        "Signature verification and A/B updates before jumping to the application.",
        "Type 3: reset to application.",
    ),
    "openblt": (
        "Open-source bootloader for automotive and embedded MCUs.",
        "Provides firmware update over CAN, USB, UART or TCP/IP, then runs the application.",
        "Type 3: reset to application with an update path.",
    ),
    "redboot": (
        "RedBoot, the eCos-based ROM monitor.",
        "Provides a debug monitor, flash management and network download, then boots an image.",
        "Type 3: it owns the board from reset.",
    ),
    "optiboot": (
        "The small AVR bootloader shipped on most Arduino boards.",
        "Occupies the boot section, accepts an STK500 upload over serial, then jumps to "
        "the sketch.",
        "Type 3: reset to application on an 8-bit MCU.",
    ),
    "Adafruit_nRF52_Bootloader": (
        "UF2 and DFU bootloader for nRF52 boards.",
        "Presents a USB mass-storage device for drag-and-drop firmware update, then "
        "starts the application.",
        "Type 3: reset to application.",
    ),
    "katapult": (
        "CAN, USB and UART bootloader for MCUs, common on 3D printer boards.",
        "Accepts firmware over its supported transports, then runs the application.",
        "Type 3: reset to application.",
    ),
    "tock-bootloader": (
        "Bootloader for the Tock embedded OS.",
        "Flashes and verifies Tock applications over serial before starting the kernel.",
        "Type 3: reset to application.",
    ),
    "STM32duino-bootloader": (
        "USB DFU bootloader for STM32F1 boards.",
        "Enumerates as a DFU device for upload, then jumps to the sketch.",
        "Type 3: reset to application.",
    ),
    "mbed-bootloader": (
        "Mbed OS bootloader with firmware update support.",
        "Verifies and applies an update image, then boots the Mbed application.",
        "Type 3: reset to application.",
    ),
    "IMBootloader": (
        "IMProject bootloader for STM32.",
        "CRC-checked firmware update over UART or USB, then application start.",
        "Type 3: reset to application.",
    ),
    "stm32-mw-openbl": (
        "STMicroelectronics OpenBootLoader middleware.",
        "Reimplements the STM32 system bootloader protocol in open source.",
        "Type 3: the in-ROM-equivalent stage that owns the MCU from reset.",
    ),
    "harmony": (
        "Microchip Harmony bootloader framework.",
        "Configurable bootloader for PIC and SAM devices with several update transports.",
        "Type 3: reset to application.",
    ),
    "arduino-variometer": (
        "Arduino variometer project including its bootloader.",
        "Application firmware with a small bootloader for a flight instrument.",
        "Type 3: reset to application on AVR.",
    ),
    "firmware": (
        "Meshtastic device firmware.",
        "ESP32 and nRF52 firmware for LoRa mesh radios, including its update path.",
        "Type 3: device firmware that owns the MCU from reset.",
    ),
}
