"""Curated prose for the wiki: what each bootloader is, how it boots, and why
it is its type.

The structural parts of a wiki page -- CVE counts, defenses, commit history --
are generated from the datasets. What cannot be generated is the explanation:
what a bootloader actually does at boot, how one stage passes state to the
next, and why that places it in Type 1, 2 or 3. That judgement lives here, one
entry per corpus project.

The `stages`, `communication` and `handoff` fields follow the structure the SoK
paper uses for its case studies (S 3): the phases a bootloader runs through,
the mechanism by which each phase reaches the next, and what is actually handed
over at the boundary. `case_study` names the paper section for the seven
bootloaders the paper covers in full.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    """One phase of a boot, and what it hands to the phase after it.

    `carries` labels the arrow leaving this stage in the generated figure, so
    it should name the artifact that crosses the boundary -- a HOB list, a
    device tree, a filled-in struct -- not repeat what the stage did.
    """

    name: str
    what: str
    carries: str


@dataclass(frozen=True)
class Bootloader:
    """One corpus project, as the wiki describes it.

    summary        one line, used on index pages
    boot_role      what it does at boot, in a sentence or two
    type_rationale why it is Type 1, 2 or 3 -- answer where it starts and what
                   it hands off to
    stages         ordered Stage records, each naming what it passes on
    target         what the last stage hands control to, for the figure
    communication  how state reaches the next stage, and how it is configured
    handoff        what is passed at the final boundary, and to whom
    case_study     SoK section number, for the bootloaders the paper details
    """

    summary: str
    boot_role: str
    type_rationale: str
    stages: tuple[Stage, ...] = ()
    target: str = ""
    communication: str = ""
    handoff: str = ""
    case_study: str = ""


BOOTLOADERS: dict[str, Bootloader] = {
    # ---- Type 1: firmware bootloaders -------------------------------------
    'coreboot': Bootloader(
        summary='Open-source replacement for proprietary x86 firmware.',
        boot_role='Runs from the reset vector, performs raw silicon and DRAM init, then hands '
                  'control to a payload (SeaBIOS, GRUB, Linux, Tianocore) that does the OS- '
                  'facing work.',
        type_rationale='Type 1: it starts from hardware with nothing initialised and '
                       'deliberately does not load an OS itself -- the payload split is the '
                       'defining Type 1 handoff.',
        case_study='3.3',
        target='Payload<br/>(SeaBIOS · GRUB · Depthcharge · UEFI)',
        stages=(
            Stage('bootblock',
                  'First code after the reset vector. Sets up temporary memory -- cache-as-RAM '
                  'on x86 -- and loads the next stage from flash.',
                  'cache-as-RAM + next stage'),
            Stage('verstage',
                  'Optional. Verifies the updatable portion of flash before it is used, '
                  'establishing the root of trust.',
                  'verified flash region'),
            Stage('romstage',
                  'Initialises the memory controller and brings up DRAM, then early chipset '
                  'setup.',
                  'DRAM up, CBMEM reserved'),
            Stage('postcar',
                  'x86 only. Tears down cache-as-RAM now that real DRAM exists, and loads '
                  'ramstage into it.',
                  'ramstage in real DRAM'),
            Stage('ramstage',
                  'The bulk of initialisation: multiprocessor bring-up, PCI enumeration, device '
                  'drivers, and construction of the coreboot table.',
                  'coreboot table + device tree'),
            Stage('SMM / BL31',
                  'Installs the trusted-firmware component -- System Management Mode on x86, or '
                  'ARM Trusted Firmware BL31 on ARM -- into memory the OS cannot reach.',
                  'SMRAM locked, EL3 resident'),
            Stage('payload',
                  'Loads and jumps to the payload, which may be a Type 1 bootloader (a UEFI '
                  'stub) or a Type 2 one (SeaBIOS, GRUB, Depthcharge).',
                  'coreboot table pointer'),
        ),
        communication='coreboot exposes no interface of its own. State reaches later stages '
                      'through CBMEM, a region carved out of the top of DRAM in romstage and '
                      'kept alive afterwards, and through the coreboot table built in ramstage: '
                      'memory ranges, serial configuration, framebuffer, and on Chromebooks the '
                      'vboot handoff and GPIO configuration. The device tree, generated at '
                      "build time from the mainboard's `devicetree.cb`, carries the static "
                      'hardware description. Anything user-facing -- NVRAM variables, an '
                      'interactive menu -- is supplied by the payload, not by coreboot.',
        handoff='ramstage loads the payload and jumps to it with a pointer to the coreboot '
                'table. How much is in that table depends on who is receiving it: a Depthcharge '
                'payload is given the full set because it is already a Type 2 loader, while a '
                'UEFI payload is given little more than memory ranges and a framebuffer because '
                'it rebuilds its own system tables from the DXE phase onward. coreboot ships '
                '`libpayload` and `BlParseLib` so the payload does not have to parse the table '
                'itself.',
    ),
    'edk2': Bootloader(
        summary="TianoCore's reference implementation of UEFI.",
        boot_role='Runs SEC, PEI, DXE and BDS phases, brings up the platform, publishes Boot '
                  'Services and Runtime Services, then selects a boot application via '
                  'BootOrder.',
        type_rationale='Type 1: it presents the hardware-agnostic UEFI interface that later '
                       'stages consume, and remains OS-agnostic -- it loads a Type 2 loader, '
                       'not a kernel.',
        case_study='3.1',
        target='Type 2 bootloader<br/>(GRUB · shim · bootmgfw.efi)',
        stages=(
            Stage('SEC (Security)',
                  'Runs from the reset vector. Sets up temporary memory, establishes the root '
                  'of trust by verifying what it loads, and finds the PEI core.',
                  'temporary memory + PEI core'),
            Stage('PEI (Pre-EFI Initialisation)',
                  'Completes CPU init and brings up permanent memory. Work is done by PEIMs, '
                  'dispatched in dependency order, which record their results as HOBs.',
                  'HOB list (memory map, FVs)'),
            Stage('DXE (Driver Execution Environment)',
                  'The core of the boot. Dispatches drivers, enumerates devices and binds '
                  'drivers to them, publishes Boot Services and Runtime Services, and sets up '
                  'SMM.',
                  'EFI System Table + protocol database'),
            Stage('BDS (Boot Device Selection)',
                  'Walks the BootOrder NVRAM variable, loads the selected boot application, and '
                  'gives the user a way to interact with the firmware.',
                  'image handle + system table pointer'),
        ),
        communication='Phases communicate through structures rather than calls. PEI passes its '
                      'findings to DXE as a HOB list -- memory ranges, firmware volumes, '
                      'platform data -- consumed once at DXE entry. From DXE onward the EFI '
                      'System Table is the interface: it points at the Boot Services table, the '
                      'Runtime Services table, the handle database of installed protocols, and '
                      'a configuration table carrying ACPI, SMBIOS and the DXE Services table. '
                      'Configuration that has to survive power-off lives in NVRAM variables '
                      '(BootOrder, Boot####, SecureBoot, PK/KEK/db), reachable through Runtime '
                      'Services. SMIs provide a channel into SMM that persists after the OS is '
                      'running.',
        handoff='BDS resolves each BootOrder entry to a device path -- a partition on a GPT '
                'disk, a network device, a USB stick -- loads the image found there, and calls '
                'it with an image handle and a pointer to the EFI System Table. That image is '
                'typically a Type 2 loader such as GRUB, shim or the Windows boot manager. When '
                'the loader is ready to start a kernel it calls `ExitBootServices()`, which '
                "frees all boot-services memory, stops the firmware's timers and drivers, and "
                'leaves only Runtime Services mapped for the OS.',
    ),
    'seabios': Bootloader(
        summary='Open-source legacy BIOS implementation, commonly a coreboot payload.',
        boot_role='Provides the 16-bit BIOS interrupt interface (int 10h, 13h, 15h) and loads '
                  'the first sector of a boot device.',
        type_rationale='Type 1: it exposes the legacy firmware interface rather than preparing '
                       'an OS, and chainloads a Type 2 loader from the MBR.',
        case_study='3.2',
        target='Type 2 bootloader<br/>(via MBR / VBR)',
        stages=(
            Stage('preinit',
                  'Runs in 16-bit real mode. Basic CPU and chipset setup, enough to get RAM '
                  'usable.',
                  'RAM usable'),
            Stage('init',
                  "Builds the firmware's data structures -- interrupt vector table, BIOS Data "
                  'Area, PCI configuration, ACPI and SMBIOS tables.',
                  'IVT + BIOS Data Area at 0x40'),
            Stage('setup',
                  'Loads option ROMs from PCI devices and runs them, so peripherals that need '
                  'their own driver code can install it.',
                  'option ROMs hooked into IVT'),
            Stage('prepboot',
                  'Finishes hardware initialisation and enumerates bootable devices: floppy, '
                  'hard disk, CD-ROM, USB, network.',
                  'bootable device list'),
            Stage('boot',
                  'Selects a boot device and invokes INT 0x19 to load and enter its boot '
                  'sector.',
                  'INT 0x19: sector at 0x7C00, DL = drive'),
        ),
        communication='SeaBIOS communicates through fixed memory locations and software '
                      'interrupts rather than tables passed by pointer. The interrupt vector '
                      'table and the BIOS Data Area at segment 0x40 are at addresses every '
                      'later stage already knows; the Extended BIOS Data Area sits just below '
                      'the 640 KB line. Services are reached by interrupt number -- INT 0x10 '
                      'for video, INT 0x13 for disk, INT 0x15 for the memory map -- and '
                      'peripherals extend the firmware by contributing option ROMs that hook '
                      'those vectors. There is no structured handoff record: the contract is '
                      'the address map itself.',
        handoff='INT 0x19 reads the first sector of the selected device to physical address '
                '0x7C00, checks for the 0xAA55 signature, and jumps there with DL set to the '
                "boot drive number. On an MBR disk that sector's 446 bytes of code find the "
                'active partition and chain to its Volume Boot Record, which loads the Type 2 '
                'bootloader. Nothing is torn down -- the interrupt services stay callable, '
                'which is exactly how a loader like GRUB reads the rest of itself off the disk.',
    ),
    'slimbootloader': Bootloader(
        summary="Intel's lightweight, fast-boot firmware for IoT and embedded x86.",
        boot_role='Stage1A/1B/2 silicon init via FSP, then launches an OS loader or payload.',
        type_rationale='Type 1: FSP-based silicon init with a payload handoff, the same '
                       'structure as coreboot.',
        target='Payload<br/>(OsLoader · UEFI payload)',
        stages=(
            Stage('Stage1A',
                  'Runs from reset out of flash. Calls the Intel FSP `TempRamInit` entry to get '
                  'cache-as-RAM, then loads Stage1B.',
                  'cache-as-RAM via FSP TempRamInit'),
            Stage('Stage1B',
                  'Calls FSP `FspMemoryInit` to bring up DRAM, verifies and loads Stage2, and '
                  'migrates state out of temporary memory.',
                  'DRAM up, HOBs migrated'),
            Stage('Stage2',
                  'Calls FSP `FspSiliconInit`, enumerates PCI, builds ACPI and SMBIOS tables, '
                  'and prepares the payload environment.',
                  'ACPI + SMBIOS tables, CFGDATA'),
            Stage('Payload',
                  'Loads a payload -- OsLoader, a UEFI payload, or a custom one -- from the '
                  'boot partition.',
                  'HOB list pointer'),
        ),
        communication="Slim Bootloader inherits EDK II's HOB mechanism: FSP returns its results "
                      'as HOBs, and each stage adds its own before passing the list on. Board '
                      'configuration is kept out of code in signed Configuration Data blobs '
                      '(CFGDATA) stored in flash, which a later stage reads rather than '
                      'recompiling for. A stage transition on this design is a verified load: '
                      'each stage measures and checks the next against keys in the key store '
                      'before jumping.',
        handoff='Stage2 hands the payload a HOB list describing memory, the serial port, the '
                'framebuffer, the performance log and the boot device. The stock OsLoader '
                'payload then locates a kernel and boots it directly; a UEFI payload instead '
                'rebuilds full UEFI services on top of what it was given, in the same way a '
                'UEFI payload does over coreboot.',
    ),
    'openbios': Bootloader(
        summary='Free IEEE 1275 Open Firmware implementation.',
        boot_role='Provides a Forth interpreter and device tree, then boots a client program.',
        type_rationale='Type 1: it is the firmware interface itself, exposing device '
                       'abstractions rather than preparing a specific OS.',
        target='Client program<br/>(OS loader)',
        stages=(
            Stage('entry and kernel bring-up',
                  'Architecture-specific entry code sets up a stack and starts the Forth '
                  'virtual machine.',
                  'Forth stack + VM running'),
            Stage('dictionary load',
                  'The compiled Forth dictionary is unpacked, giving the interpreter its '
                  'vocabulary.',
                  'interpreter vocabulary'),
            Stage('device probing',
                  'Drivers probe buses and instantiate packages, building the IEEE 1275 device '
                  'tree under /packages.',
                  'IEEE 1275 device tree'),
            Stage('client interface',
                  'The Open Firmware client interface is published and a boot device is '
                  'selected, then the client program is loaded and entered.',
                  'client interface entry point'),
        ),
        communication='Everything is the device tree. Each node carries properties -- `reg`, '
                      '`compatible`, `device_type` -- and methods callable through the '
                      'interface, so a later stage discovers hardware by walking the tree '
                      'rather than by being handed a table. Persistent configuration lives in '
                      'NVRAM: `boot-device`, `boot-args`, and `nvramrc`, a Forth script run at '
                      'start-up that can patch the tree before anything else sees it. The Forth '
                      'dictionary itself is state, so a client can define and call new words at '
                      'runtime.',
        handoff='OpenBIOS loads the client program and enters it with a pointer to the client '
                'interface handler in a well-known register. The client keeps calling back into '
                'firmware -- `finddevice`, `getprop`, `claim`, `read` -- to walk the tree and '
                'allocate memory, which is why the firmware stays resident rather than being '
                'torn down. The OS takes ownership when it stops making those calls.',
    ),
    'openfirmware': Bootloader(
        summary="Mitch Bradley's original IEEE 1275 Open Firmware.",
        boot_role='Forth-based firmware providing device discovery, a device tree and a client '
                  'interface for the OS loader.',
        type_rationale='Type 1: the canonical hardware-agnostic firmware interface.',
        target='Client program<br/>(OS loader)',
        stages=(
            Stage('reset and Forth bring-up',
                  'Processor-specific reset code initialises memory and starts the Forth '
                  'kernel.',
                  'Forth kernel running'),
            Stage('device tree construction',
                  'Probing creates the device tree; FCode drivers in expansion ROMs are '
                  'interpreted and add their own nodes.',
                  'device tree + FCode drivers'),
            Stage('user interface',
                  'The `ok` prompt is available, allowing the tree to be inspected and boot '
                  'variables changed.',
                  'NVRAM boot variables'),
            Stage('boot',
                  '`boot` loads the client program named by `boot-device` and transfers to it '
                  'through the client interface.',
                  'client interface entry point'),
        ),
        communication='This is the implementation the IEEE 1275 standard was written from, and '
                      "the mechanisms are the standard's: a device tree of nodes with "
                      'properties and methods, NVRAM configuration variables, and FCode -- '
                      "tokenised Forth carried in a card's ROM -- so a plug-in device can "
                      'describe and drive itself to firmware that has never seen it. Because '
                      'the interpreter is present throughout, the boundary between stages is a '
                      'vocabulary boundary rather than a binary one.',
        handoff='The client program is entered with the client-interface entry point in a '
                'register defined per architecture. It calls back for device access and memory '
                'claims until it has loaded the kernel, at which point it stops calling and the '
                "firmware's resources may be reclaimed. On SPARC and PowerPC this same "
                'interface is what the OS kernel reads its device tree from.',
    ),
    'hostboot': Bootloader(
        summary='IBM OpenPOWER host firmware.',
        boot_role='Initialises POWER processors and memory from the service processor handoff, '
                  'then loads skiboot.',
        type_rationale='Type 1: bare-hardware bring-up that hands off to a separate OS-facing '
                       'stage.',
        target='Payload<br/>(skiboot · PHYP)',
        stages=(
            Stage('SBE',
                  "The Self-Boot Engine, running on the processor's on-chip controller, "
                  'initialises the first core and loads the Hostboot base image.',
                  'first core up, HBBL loaded'),
            Stage('HBBL (bootloader)',
                  'A small loader that verifies the base image and unpacks it into L3 cache '
                  'configured as memory, because DRAM does not exist yet.',
                  'verified base image in L3 cache'),
            Stage('HBB (base image)',
                  'Sets up the kernel, tasks and the targeting model that describes every piece '
                  'of hardware in the system.',
                  'targeting model + istep engine'),
            Stage('isteps',
                  'A long sequence of numbered initialisation steps -- clocks, buses, memory '
                  'training, PCIe -- each one a discrete, restartable unit.',
                  'trained DRAM, attributes in PNOR'),
            Stage('payload load',
                  'Builds the hardware description and loads the payload (skiboot or PHYP) into '
                  'DRAM.',
                  'HDAT + device tree in memory'),
        ),
        communication="Hostboot's stages share a targeting model: an attribute database of "
                      'hardware targets, persisted to PNOR, which every istep reads and '
                      'updates. Because the isteps are numbered and their state is '
                      'externalised, a failed boot can be resumed or a deconfiguration recorded '
                      'and carried forward. Communication with the service processor runs over '
                      'a mailbox, and the result of the whole sequence is serialised into HDAT, '
                      'the structured hardware description the payload consumes.',
        handoff='Hostboot places HDAT structures and the device tree in memory, then jumps to '
                'the payload it loaded -- skiboot on OpenPOWER, PHYP on PowerVM. It does not '
                'disappear: Hostboot runtime services stay resident to handle attribute access '
                'and error logging for the payload and the OS.',
    ),
    'lbmk': Bootloader(
        summary="Libreboot's build system, packaging coreboot with free payloads.",
        boot_role='Produces coreboot images with GRUB or SeaBIOS payloads for supported '
                  'machines.',
        type_rationale='Type 1: a distribution of Type 1 firmware; the payload it bundles is '
                       'Type 2.',
        target='Operating system',
        stages=(
            Stage('(build system)',
                  "lbmk assembles the boot firmware; at runtime the flow is coreboot's -- "
                  'bootblock, romstage, ramstage -- followed by the payload lbmk configured.',
                  'coreboot image + payload, flashed'),
        ),
        communication="Libreboot's contribution is at build time rather than boot time: it "
                      'fetches coreboot, patches it, supplies the board configuration, and '
                      'packages a payload -- SeaBIOS, GRUB, U-Boot or a chain of them. Runtime '
                      'communication is whatever that combination uses; with the common '
                      "SeaBIOS-plus-GRUB arrangement, coreboot's table reaches SeaBIOS, and "
                      'SeaBIOS then exposes the legacy interrupt interface that GRUB uses.',
        handoff="The handoff is coreboot's payload jump, and then the payload's own. The "
                'property Libreboot adds is what is *absent* from the image -- no Intel ME, no '
                'proprietary blobs on supported boards -- which is a supply-chain property of '
                'the artefact rather than a step in the boot flow.',
    ),
    'firmware-open': Bootloader(
        summary="System76's open firmware distribution.",
        boot_role='coreboot plus EDK-II payload and System76 EC firmware for their laptops.',
        type_rationale='Type 1: vendor packaging of Type 1 firmware.',
        target='Operating system',
        stages=(
            Stage('coreboot bootblock/romstage/ramstage',
                  'Silicon and memory initialisation, using Intel FSP binaries for the parts '
                  'that are not open.',
                  'coreboot table'),
            Stage('EC firmware',
                  'Separately built firmware for the embedded controller, handling power '
                  'sequencing, keyboard and thermals alongside the main boot.',
                  'power sequencing over eSPI'),
            Stage('EDK II payload',
                  "A UEFI payload runs as coreboot's payload, publishing UEFI services for the "
                  'OS.',
                  'UEFI services rebuilt from BlParseLib'),
            Stage('boot application',
                  "The UEFI payload's BDS phase loads the distribution's bootloader from the "
                  'EFI system partition.',
                  'system table pointer'),
        ),
        communication='Two mechanisms meet here. coreboot hands the payload a coreboot table '
                      'describing memory and the framebuffer; the EDK II payload reads that '
                      'table through `BlParseLib` and rebuilds it as UEFI HOBs and system '
                      'tables, so the OS sees a normal UEFI machine. The EC runs its own '
                      'firmware and communicates with the host over the LPC/eSPI interface, out '
                      'of band from the boot sequence.',
        handoff="The final handoff is UEFI's: the payload's BDS phase loads a boot application "
                "from the ESP and calls `ExitBootServices()`. System76's firmware update path "
                'also runs through this image, which is why the EC firmware is versioned with '
                'it.',
    ),
    'LakeBIOS': Bootloader(
        summary='Minimal experimental x86 BIOS implementation.',
        boot_role='Brings up a QEMU-class machine and provides a minimal BIOS interface.',
        type_rationale='Type 1: firmware-level bring-up from reset.',
        target='Type 2 bootloader',
        stages=(
            Stage('reset entry',
                  'Executes from the reset vector in flash and sets up an environment for C '
                  'code.',
                  'C environment ready'),
            Stage('chipset initialisation',
                  'Brings up the emulated northbridge/southbridge -- QEMU I440FX-PIIX and '
                  'Q35-ICH9 are the supported targets.',
                  'chipset up'),
            Stage('device setup',
                  'Enumerates and configures PCI devices, bridges, disk controllers and '
                  'displays through a hardware abstraction layer.',
                  'PCI devices configured'),
            Stage('frontend',
                  'A legacy BIOS frontend presents the interface the next stage expects; UEFI- '
                  'style services are a work in progress.',
                  'legacy interrupt interface'),
        ),
        communication='LakeBIOS is a small, deliberately modular reimplementation, and its '
                      'internal boundary is the HAL rather than a table format. Where it '
                      'presents a legacy frontend, communication with the next stage follows '
                      'the BIOS conventions -- interrupt vectors and fixed low-memory '
                      'structures -- described under [seabios](bootloader:seabios).',
        handoff='As a legacy frontend it chainloads through the boot sector in the usual way. '
                'It is a research and teaching implementation rather than production firmware, '
                'so its value in this corpus is as a minimal, readable example of the Type 1 '
                'structure.',
    ),
    'oreboot': Bootloader(
        summary='coreboot rewritten in Rust, with no C.',
        boot_role='Performs silicon init and hands to a payload, targeting RISC-V and ARM as '
                  'well as x86.',
        type_rationale='Type 1: same role and payload handoff as coreboot, different language.',
        target='LinuxBoot payload<br/>(kernel + u-root)',
        stages=(
            Stage('bt0',
                  'First-stage ROM code in Rust: minimal clock and pin setup, enough to load '
                  'the next stage.',
                  'clocks set, next stage loaded'),
            Stage('bt1 / main',
                  'Memory controller initialisation and the remaining platform bring-up.',
                  'DRAM up'),
            Stage('mainboard',
                  'Board-specific setup, then preparation of the payload environment.',
                  'board setup complete'),
            Stage('payload',
                  'Loads a LinuxBoot payload -- a Linux kernel with a u-root initramfs -- and '
                  'jumps to it.',
                  'device tree pointer'),
        ),
        communication='oreboot is coreboot with the C removed, and it deliberately dropped '
                      "coreboot's table-passing machinery along with it. Where coreboot builds "
                      'a coreboot table for an arbitrary payload, oreboot targets LinuxBoot and '
                      'passes what a Linux kernel expects: a device tree on ARM and RISC-V. '
                      'Stage boundaries are Rust crates linked into separate images rather than '
                      'modules dispatched at runtime.',
        handoff="The payload is a Linux kernel, entered with the architecture's normal boot "
                "protocol -- device tree pointer in the expected register. From there u-root's "
                'Go userland performs what a Type 2 bootloader would otherwise do, including '
                'kexec into the target kernel.',
    ),
    'mu_basecore': Bootloader(
        summary="Microsoft's Project Mu fork of EDK-II.",
        boot_role='Supplies the core UEFI packages that Mu platform repositories build against; '
                  'ships on Surface devices and Hyper-V.',
        type_rationale='Type 1: a UEFI implementation. Note it is a library repository, not a '
                       'standalone buildable platform.',
        target='Type 2 bootloader',
        stages=(
            Stage('SEC',
                  'As in EDK II: reset-vector code, temporary memory, root of trust.',
                  'temporary memory + PEI core'),
            Stage('PEI',
                  'Permanent memory bring-up through PEIMs, results recorded as HOBs.',
                  'HOB list'),
            Stage('DXE',
                  'Driver dispatch, device enumeration, Boot and Runtime Services.',
                  'EFI System Table + policy service'),
            Stage('BDS',
                  'Boot device selection from NVRAM variables.',
                  'image handle + system table pointer'),
        ),
        communication='Project Mu is a fork of EDK II, so the communication mechanisms are EDK '
                      "II's: HOB list from PEI to DXE, the EFI System Table and protocol "
                      'database from DXE onward, and NVRAM variables for persistent '
                      'configuration. What Mu adds is policy and structure around them -- a '
                      'policy service for cross-module settings, and package boundaries '
                      'maintained so platforms consume Mu as a versioned dependency instead of '
                      'forking the tree.',
        handoff='Identical to EDK II: BDS loads a boot application from the EFI system '
                'partition with a pointer to the system table, and `ExitBootServices()` marks '
                'the transition to the OS. In practice mu_basecore is not built alone -- a '
                'platform repository supplies the silicon and board packages that complete the '
                'image.',
    ),
    'edk2-platforms': Bootloader(
        summary='Board support built on EDK-II.',
        boot_role='Platform-specific PEI/DXE modules for real silicon, consumed with edk2.',
        type_rationale='Type 1: the platform half of a UEFI firmware image.',
        target='Firmware image<br/>(built with edk2)',
        stages=(
            Stage('(no independent boot flow)',
                  'Supplies the platform, silicon and driver packages that a UEFI firmware '
                  "image is built from; the SEC/PEI/DXE/BDS flow is EDK II's.",
                  'PEIMs, DXE drivers and PCDs, linked at build time'),
        ),
        communication="The packages here plug into EDK II's existing mechanisms rather than "
                      'defining new ones: PEIMs that publish HOBs, DXE drivers that install '
                      'protocols, and PCDs -- build- or runtime-configurable values -- that a '
                      'platform sets to select behaviour without editing core code.',
        handoff='There is no handoff of its own. A platform in this tree is compiled together '
                'with edk2 into one firmware image, and that image performs the UEFI handoff '
                'described under [edk2](bootloader:edk2).',
    ),
    'opensbi': Bootloader(
        summary='RISC-V Supervisor Binary Interface reference implementation.',
        boot_role='Runs in M-mode, sets up the machine, provides the SBI ABI, then enters '
                  'S-mode at the next stage.',
        type_rationale='Type 1: it is the privileged firmware layer presenting a stable '
                       "interface to whatever boots next -- the RISC-V analogue of UEFI's role.",
        target='S-mode payload<br/>(U-Boot · Linux)',
        stages=(
            Stage('_start',
                  'The first hart enters the firmware; others are held in a wait loop. Sets up '
                  'the stack and the per-hart scratch space.',
                  'per-hart scratch space'),
            Stage('cold boot path',
                  'The boot hart relocates the firmware if needed, initialises the console and '
                  'platform, and parses the device tree.',
                  'console + parsed device tree'),
            Stage('warm boot path',
                  'Each remaining hart initialises its own trap handling, timers and interrupt '
                  'controller.',
                  'traps and timers per hart'),
            Stage('sbi_init',
                  'Registers ecall extensions (timer, IPI, HSM, reset) and defines the domains '
                  'that partition memory and devices.',
                  'SBI extensions + domains, PMP set'),
            Stage('next stage',
                  "Configures PMP for the next stage's domain and drops from M-mode to S-mode "
                  "at the payload's entry point.",
                  'mret: a0 = hartid, a1 = FDT'),
        ),
        communication='OpenSBI passes forward a device tree, which it may edit first -- '
                      'reserving its own memory so the next stage does not use it, and adding '
                      'nodes for what it manages. After the transition the interface is not a '
                      'table but the `ecall` instruction: the S-mode payload traps into M-mode '
                      'for timers, IPIs, hart state management and system reset. The three '
                      'build shapes differ only in where the next stage comes from: FW_JUMP '
                      'jumps to a fixed address, FW_PAYLOAD embeds the next stage in the '
                      'firmware image, and FW_DYNAMIC takes its parameters from a struct the '
                      'previous loader filled in.',
        handoff='The handoff is an `mret` into S-mode with `a0` set to the hart ID and `a1` to '
                'the physical address of the device tree -- the same convention the Linux '
                'RISC-V kernel expects. PMP entries are programmed first so the supervisor '
                'cannot reach firmware memory. OpenSBI stays resident in M-mode for the life of '
                'the system.',
    ),
    # ---- Type 2: OS bootloaders -------------------------------------------
    'grub': Bootloader(
        summary='GNU GRUB 2, the dominant Linux boot loader.',
        boot_role='Reads grub.cfg, offers a menu and a scripting shell, loads a kernel and '
                  'initrd from a filesystem, and boots it or chainloads another loader.',
        type_rationale='Type 2: it starts from an already-initialised machine, is driven '
                       'entirely by on-disk configuration, and its whole purpose is preparing '
                       'an OS.',
        case_study='3.5',
        target='Operating system<br/>(Linux · chainloaded loader)',
        stages=(
            Stage('boot.img',
                  '512 bytes in the MBR. Its only job is to read the first sector of core.img, '
                  'whose location was written into it at install time.',
                  'sector address of core.img'),
            Stage('core.img',
                  'The working bootloader: kernel.img plus the handful of modules needed to '
                  'reach /boot -- a disk driver, a partition map parser, a filesystem driver.',
                  'decompressed into memory'),
            Stage('kernel.img',
                  "GRUB's core services: memory management, the device and filesystem "
                  'abstraction, environment variables, the rescue shell.',
                  'device + filesystem abstraction'),
            Stage('module load',
                  'Modules (*.mod) are loaded on demand from /boot/grub for filesystems, '
                  'compression, video, cryptography and boot protocols.',
                  'commands registered by modules'),
            Stage('grub.cfg',
                  'The menu and its entries are read and executed as a script, which selects a '
                  'kernel and its arguments.',
                  'kernel + initrd + command line'),
        ),
        communication="GRUB's stage boundaries exist because of a size limit, not a privilege "
                      'boundary: each stage is the smallest thing that can find the next one. '
                      'Once kernel.img is running, configuration moves into text -- `grub.cfg`, '
                      'plus the environment block at `/boot/grub/grubenv` for values that must '
                      'survive a reboot, such as the saved default entry and `recordfail`. '
                      'Modules communicate through the command table they register into, which '
                      'is why a menu entry can `insmod` a filesystem driver and then use it in '
                      'the next line. On a UEFI machine the first two stages collapse: the '
                      'firmware loads `grubx64.efi`, a single image with the modules already '
                      'built in.',
        handoff='A menu entry ends in a boot protocol command. `linux` loads a kernel and '
                '`initrd` its initial ramdisk, then GRUB assembles the boot parameters -- '
                '`root=UUID=...`, console settings, everything on the kernel command line -- '
                'calls `ExitBootServices()` if it is running under UEFI, and enters the kernel. '
                '`multiboot` does the same for a Multiboot2 kernel, passing a structured '
                'information table. `chainloader` instead loads another bootloader, which is '
                'how GRUB reaches the Windows boot manager.',
    ),
    'shim': Bootloader(
        summary='Signed first-stage UEFI loader that extends Secure Boot to distro keys.',
        boot_role='Verifies and loads the next stage (usually GRUB) against its own key '
                  'database and SBAT revocation levels.',
        type_rationale='Type 2: it runs on top of UEFI firmware and exists solely to get an OS '
                       'loader trusted and running.',
        target='Second-stage loader<br/>(grubx64.efi)',
        stages=(
            Stage('loaded by firmware',
                  "The firmware's BDS phase loads shimx64.efi, which is signed by a key already "
                  "in the platform's db.",
                  'image handle + system table'),
            Stage('certificate and policy setup',
                  'shim installs its own verification protocol and reads MokList, MokListX and '
                  'the built-in vendor certificate.',
                  'vendor cert + MokList loaded'),
            Stage('MokManager',
                  'If enrolment is pending, MokManager.efi runs first so the user can approve a '
                  'key or hash at the console.',
                  'newly enrolled keys'),
            Stage('second-stage load',
                  'Verifies and loads the real bootloader -- usually grubx64.efi -- from the '
                  'same directory.',
                  'Shim Lock protocol installed'),
            Stage('fallback',
                  'If no boot variable points anywhere valid, fallback.efi rebuilds the '
                  'Boot#### entries from BOOTX64.CSV.',
                  'rebuilt Boot#### entries'),
        ),
        communication="shim exists to move the trust decision out of the firmware's key "
                      'database and into one the distribution controls. It passes its '
                      'verification service forward by installing the Shim Lock protocol into '
                      'the UEFI handle database, so the loader it starts -- and the Linux '
                      'kernel after that -- can ask shim to verify an image against the vendor '
                      'certificate or the Machine Owner Key list instead of against the '
                      "firmware's db. Those MOK lists live in UEFI variables, written only "
                      'through MokManager at the console, which is what keeps a running OS from '
                      'silently enrolling its own key.',
        handoff='shim loads the next binary with the ordinary UEFI image services and calls it '
                "with the same system table it was given, so from the second-stage loader's "
                'point of view nothing has changed except that a verification protocol is now '
                "available. Control continues to GRUB, which starts the kernel; the kernel's "
                "lockdown mode then consults shim's variables to decide whether Secure Boot is "
                'in force.',
    ),
    'systemd': Bootloader(
        summary='systemd, whose systemd-boot is a minimal UEFI boot manager.',
        boot_role='Enumerates boot entries from the EFI System Partition and launches the '
                  'chosen kernel, with no scripting language.',
        type_rationale='Type 2: a UEFI application that selects and starts an OS.',
        target='Linux kernel',
        stages=(
            Stage('systemd-boot',
                  'A UEFI boot manager loaded by the firmware. It reads loader entries from the '
                  'ESP and presents a menu.',
                  'menu selection'),
            Stage('loader entries',
                  'Plain text files under /loader/entries name a kernel, an initrd and a '
                  'command line, or a single unified kernel image.',
                  'kernel path, initrd, cmdline'),
            Stage('stub (UKI)',
                  'systemd-stub is linked into a unified kernel image so the kernel, initrd, '
                  'command line and signature ship as one signed PE binary.',
                  'signed PE with cmdline inside'),
            Stage('kernel start',
                  'The chosen kernel is loaded and entered through the EFI stub.',
                  'boot params + TPM measurements'),
        ),
        communication='systemd-boot deliberately does nothing the firmware already does: it has '
                      'no filesystem drivers of its own and reads only the FAT ESP the firmware '
                      'can already see. State passes as UEFI variables in the vendor GUID '
                      '`4a67b082-0a4c-41cf-b6c7-440b29bb8c4f` -- `LoaderEntryDefault`, '
                      '`LoaderEntryOneShot` for a single alternate boot, `LoaderTimeInitUSec` '
                      'for the timing the OS later reports -- so `bootctl` in userspace and the '
                      'boot manager agree without a private configuration format. A unified '
                      'kernel image goes further and removes the gap entirely: because the '
                      'command line is inside the signed PE image, it cannot be edited between '
                      'verification and use.',
        handoff='The kernel is started through the EFI stub with the boot parameters the entry '
                'specified, and `ExitBootServices()` is called by the stub. systemd-stub '
                'additionally passes the initrd and any addons through the LINUX_INITRD_MEDIA '
                'device path protocol, and measures what it loaded into the TPM so the sequence '
                'can be attested afterwards.',
    ),
    'limine': Bootloader(
        summary='Modern multi-protocol bootloader for x86 and aarch64.',
        boot_role='Supports its own protocol plus Linux, Multiboot and chainloading, from BIOS '
                  'or UEFI.',
        type_rationale='Type 2: boots from an initialised platform into an OS kernel.',
        target='Kernel<br/>(Limine · Multiboot · Linux)',
        stages=(
            Stage('stage1',
                  'On BIOS, a 512-byte MBR/VBR stage that loads stage2. On UEFI, the firmware '
                  'loads BOOTX64.EFI directly and this stage does not exist.',
                  'stage2 loaded from disk'),
            Stage('stage2',
                  'Decompresses and enters the main bootloader image.',
                  'decompressed bootloader'),
            Stage('common',
                  'The bootloader proper: filesystem drivers, the config parser, the menu and '
                  'the terminal.',
                  'config parsed, kernel loaded'),
            Stage('protocol handler',
                  'Loads the kernel according to the protocol it asks for -- Limine, '
                  'Multiboot1/2, Linux or chainload.',
                  'filled request/response structs, paging on'),
        ),
        communication='Configuration is a single `limine.conf` on the boot partition. What '
                      'distinguishes Limine is the shape of the handoff rather than the '
                      'configuration: instead of one information structure, the kernel embeds a '
                      'list of *request* structures, each tagged with a magic number, and the '
                      'bootloader scans the loaded image for them and fills in the responses it '
                      'recognises. A kernel asks only for what it needs -- memory map, '
                      'framebuffer, higher-half direct map, SMP -- and the two sides stay '
                      'compatible as the protocol grows.',
        handoff='The kernel is entered in a defined state: 64-bit long mode already on, its own '
                'page tables installed with the higher-half direct map in place, a stack '
                'allocated, and the response structures filled in. Under UEFI, '
                '`ExitBootServices()` has already been called. Multiboot and Linux kernels are '
                'booted with their own protocols instead.',
    ),
    'refind': Bootloader(
        summary='Graphical UEFI boot manager.',
        boot_role='Scans partitions for boot loaders and kernels and presents a menu.',
        type_rationale='Type 2: a UEFI boot manager whose job is choosing and launching an OS.',
        target='Loader or kernel<br/>(EFI stub · bootmgfw.efi)',
        stages=(
            Stage('loaded by firmware',
                  'refind_x64.efi is loaded from the ESP as a UEFI application, often in place '
                  "of the distribution's own loader.",
                  'image handle + system table'),
            Stage('configuration and driver load',
                  'Reads refind.conf, then loads filesystem drivers from drivers_x64/ so it can '
                  'read partitions the firmware cannot.',
                  'filesystem drivers installed'),
            Stage('scan',
                  'Scans volumes for loaders, kernels and OS signatures, and builds a menu '
                  'automatically from what it finds.',
                  'discovered loaders and kernels'),
            Stage('launch',
                  'Starts the selected image, or a kernel directly if it has an EFI stub.',
                  'image handle + system table'),
        ),
        communication='rEFInd is a boot *manager*: the intelligence is in discovery rather than '
                      'in loading. Its optional UEFI filesystem drivers extend what the '
                      'firmware itself can read, which is how it lists kernels on ext4 or '
                      'Btrfs. Configuration is `refind.conf` plus per-kernel option files '
                      '(`refind_linux.conf`), and it can consult `/etc/fstab` to work out the '
                      'correct `root=` argument rather than being told.',
        handoff='A menu selection is a normal UEFI image load: the target gets its own image '
                'handle and the same system table. For a Linux kernel built with the EFI stub '
                'that target is the kernel itself, so the chain is firmware to rEFInd to kernel '
                "with no second loader. For Windows or macOS it is the vendor's own loader. "
                'When Secure Boot is in force, rEFInd is normally launched by shim so its own '
                'launches can be verified.',
    ),
    'ipxe': Bootloader(
        summary='Open-source network boot firmware.',
        boot_role='Provides PXE and its own scripting, fetching kernels over HTTP, iSCSI or '
                  'Infiniband and booting them.',
        type_rationale='Type 2: it runs as an option ROM or UEFI application on an initialised '
                       'machine and loads an OS over the network.',
        target='Kernel or chainloaded loader',
        stages=(
            Stage('ROM or image entry',
                  'Runs as a PCI option ROM, a UEFI driver, or an image chainloaded by another '
                  'bootloader.',
                  'NIC reachable'),
            Stage('driver and stack bring-up',
                  'Initialises the network card, then its own TCP/IP stack, DHCP client and '
                  'TLS.',
                  'DHCP lease + settings tree'),
            Stage('script execution',
                  'Runs an embedded or downloaded iPXE script, which decides what to boot.',
                  'chosen URL and boot method'),
            Stage('image load',
                  'Fetches the target over HTTP, HTTPS, iSCSI, FCoE, AoE or NFS and loads it '
                  'into memory.',
                  'image in memory'),
            Stage('boot',
                  'Starts the loaded image, or exposes a remote volume as a local disk and '
                  'boots from that instead.',
                  'kernel + cmdline, or hooked INT 13h'),
        ),
        communication="iPXE replaces PXE's TFTP-only path with a full network stack, and its "
                      'state is the DHCP option space plus its own settings tree: values such '
                      'as `${net0/mac}`, `${filename}` and custom options are readable in '
                      'scripts and substituted into URLs. Scripts are fetched over the network, '
                      'so the boot decision can be made by a server per machine. Because it can '
                      'present an iSCSI or AoE target as an INT 0x13 drive (or a UEFI block '
                      'device), an OS installer that knows nothing about the network can '
                      'install onto a remote volume.',
        handoff='How control transfers depends on the target: a Linux kernel is started with '
                'its command line and initrd, another bootloader is chainloaded, or -- in the '
                'SAN case -- iPXE stays resident, hooks the disk interface, and hands off to a '
                'boot sector that reads what is actually a remote block device. That last mode '
                'means iPXE is still executing while the OS believes it is talking to local '
                'storage.',
    ),
    'depthcharge': Bootloader(
        summary='ChromeOS bootloader, a coreboot payload.',
        boot_role='Implements Chrome OS verified boot, selects a kernel partition and boots it.',
        type_rationale='Type 2: it is the payload that coreboot (Type 1) hands off to, and it '
                       'prepares an OS.',
        target='Linux kernel<br/>(ChromeOS)',
        stages=(
            Stage('loaded as coreboot payload',
                  "coreboot's ramstage loads depthcharge and passes it the coreboot table, "
                  'including the vboot handoff block.',
                  'coreboot table + vboot handoff'),
            Stage('vboot verification',
                  'Verifies the kernel partition signature against keys in the GBB and the '
                  "TPM's rollback counters.",
                  'verified kernel partition, TPM counters'),
            Stage('recovery or normal mode',
                  'Chooses between normal boot, developer mode, and recovery from removable '
                  'media, based on the firmware switches.',
                  'selected boot mode'),
            Stage('kernel load',
                  'Loads the signed kernel partition from eMMC, NVMe or USB.',
                  'kernel image in memory'),
            Stage('boot',
                  'Assembles the command line and starts the kernel.',
                  'cmdline with dm-verity root'),
        ),
        communication='Depthcharge is built for one platform family, so it takes far more from '
                      'coreboot than a general payload does: the coreboot table it receives '
                      'carries GPIO configuration, board identity and the vboot handoff '
                      'structure recording what verstage already decided. Rollback protection '
                      'is anchored in TPM NVRAM -- the kernel version in the signed header must '
                      'be at least the value stored there -- so the state that matters most '
                      "between boots lives in the TPM rather than in flash. ChromeOS's A/B "
                      'partitioning and the `successful`/`tries` GPT attribute bits are what '
                      'the update system and the bootloader use to agree on which slot to '
                      'trust.',
        handoff='The kernel is entered directly with a command line that names the verified '
                'root and its dm-verity hash tree, so integrity checking continues into the '
                'running system. There is no Type 2 loader in between and no menu; the disk '
                'layout and the signature decide.',
    ),
    'lk': Bootloader(
        summary='Little Kernel, a small embedded OS used as a bootloader.',
        boot_role='Used by Qualcomm as the Android aboot bootloader: initialises minimal '
                  'hardware, verifies and boots the Android boot image.',
        type_rationale="Type 2 in this corpus: it runs after the SoC's primary bootloader has "
                       'brought the platform up, and loads an OS. Arguably Type 3 on platforms '
                       'where it is the only stage.',
        target='Android kernel',
        stages=(
            Stage('reset and platform early init',
                  'Architecture entry code sets up the MMU, caches and stack, then calls '
                  'platform early init.',
                  'MMU, caches, stack'),
            Stage('kernel init',
                  'Brings up the threading kernel, timers and heap -- LK is a small preemptive '
                  'kernel, not just a loader.',
                  'threads, timers, heap'),
            Stage('target init',
                  'Board-specific initialisation: display, storage, USB.',
                  'storage, USB, display'),
            Stage('app start',
                  'Starts the built-in application, which on a phone is the aboot bootloader '
                  'app.',
                  'boot image + cmdline, ARM protocol'),
        ),
        communication='LK is a kernel first and a bootloader second, so its stages are module '
                      'init levels rather than separate binaries: drivers register init hooks '
                      'at a declared level and the kernel calls them in order, all within one '
                      'image. As a bootloader its external interface is Fastboot over USB -- '
                      'flashing, `boot`, `oem` commands -- and the shared memory and SMEM '
                      'structures the Qualcomm firmware left behind, which tell it the board '
                      'identity and why the device reset.',
        handoff='The aboot application parses an Android boot image -- kernel, ramdisk and a '
                'device tree appended or selected from a dtbo partition -- verifies it if '
                'verified boot is enabled, assembles the kernel command line with the boot mode '
                'and serial number, and jumps to the kernel with the ARM boot protocol. On '
                'modern Qualcomm devices this role has moved into ABL under UEFI, so LK is '
                'mainly seen on older hardware.',
    ),
    'lk2nd': Bootloader(
        summary='Second-stage LK bootloader for msm8916 mainline Linux.',
        boot_role='Loads from the stock aboot and boots mainline Linux with a proper device '
                  'tree.',
        type_rationale='Type 2: explicitly a second stage that prepares an OS.',
        target='Mainline kernel',
        stages=(
            Stage('stock bootloader',
                  "The device's own LK or ABL loads lk2nd as if it were an Android boot image.",
                  'loaded as an Android boot image'),
            Stage('hardware detection',
                  'Identifies the board, display panel and battery from the SMEM and device '
                  'tree information the firmware left.',
                  'board, panel and battery IDs from SMEM'),
            Stage('device tree fixup',
                  'Patches or selects a device tree matching what it detected.',
                  'patched device tree'),
            Stage('menu and boot',
                  'Offers Fastboot and a menu, then boots a kernel from a partition, a '
                  'filesystem or an SD card.',
                  'kernel + fixed-up DTB'),
        ),
        communication='lk2nd is a second-stage bootloader: it is installed where the vendor '
                      'expects a kernel, so its input is the Android boot image format, and its '
                      "job is to undo the vendor's assumptions before the real kernel sees "
                      'them. The important state is what the proprietary firmware left in SMEM '
                      '-- board ID, panel ID, charger status -- which lk2nd reads and '
                      'translates into a device tree and command line a mainline kernel can '
                      'use.',
        handoff='It boots a kernel with the standard ARM protocol, passing the fixed-up device '
                'tree it assembled. Because it re-implements Fastboot, it also gives devices '
                'with a hostile or crippled vendor bootloader a consistent flashing interface, '
                'which is the practical reason postmarketOS uses it.',
    ),
    'skiboot': Bootloader(
        summary='OPAL firmware for OpenPOWER.',
        boot_role='Loaded by hostboot, provides OPAL runtime services and boots a Linux kernel '
                  'via petitboot.',
        type_rationale="Type 2: it starts from hostboot's initialised state and prepares an OS.",
        target='Payload<br/>(Linux running Petitboot)',
        stages=(
            Stage('entry from Hostboot',
                  'Hostboot loads skiboot into memory and enters it with a pointer to the HDAT '
                  'hardware description.',
                  'HDAT pointer'),
            Stage('HDAT parse',
                  'Converts HDAT into a flattened device tree describing processors, memory, '
                  'PCIe and service interfaces.',
                  'flattened device tree'),
            Stage('hardware init',
                  'Initialises PCIe, the interrupt controller, NVRAM and the console.',
                  'PCIe, interrupts, NVRAM up'),
            Stage('OPAL publication',
                  'Registers the OPAL runtime call interface the OS will use.',
                  'OPAL call interface registered'),
            Stage('payload boot',
                  'Loads the payload from PNOR -- normally a Linux kernel running Petitboot -- '
                  'and enters it.',
                  'r3 = device tree, /ibm,opal node'),
        ),
        communication="skiboot's input is HDAT and its output is a device tree, and that "
                      'translation is most of what it does: everything the OS learns about the '
                      'machine arrives as device tree nodes and properties. After the handoff, '
                      'communication is OPAL calls -- an `OPAL_CALL` into firmware for console, '
                      'PCI, NVRAM, sensors and error logging -- plus an asynchronous message '
                      'queue the OS polls. skiboot stays resident in hypervisor-privileged '
                      'memory for the life of the system.',
        handoff='The kernel is entered with `r3` pointing at the flattened device tree, in '
                "which the `/ibm,opal` node tells the OS the firmware's entry point and base. "
                'That kernel is usually not the final OS but a small Linux running Petitboot, '
                'which then kexecs into the real one.',
    ),
    'petitboot': Bootloader(
        summary='kexec-based bootloader for OpenPOWER.',
        boot_role='Runs in a small Linux environment, discovers boot options and kexecs the '
                  'target kernel.',
        type_rationale='Type 2: it runs on an initialised platform and its only job is '
                       'launching an OS.',
        target='Target OS kernel',
        stages=(
            Stage('Linux userspace start',
                  'Petitboot runs on a small Linux already booted by the platform firmware, so '
                  'the kernel and drivers are in place before it starts.',
                  'running kernel + drivers'),
            Stage('device discovery',
                  'udev events drive discovery: disks are mounted, network interfaces '
                  'configured by DHCP.',
                  'mounted disks, DHCP leases'),
            Stage('configuration parsing',
                  'Existing bootloader configurations found on those devices -- grub.cfg, '
                  'syslinux.cfg, PXE config -- are parsed into boot options.',
                  'parsed boot options'),
            Stage('user interface',
                  'An ncurses UI lists what was found, with a timeout for automatic boot.',
                  'user selection (or timeout)'),
            Stage('kexec',
                  'The chosen kernel and initrd are loaded and kexec replaces the running '
                  'kernel.',
                  'kexec: kernel + initrd + cmdline'),
        ),
        communication='Petitboot inverts the usual arrangement: because a full Linux is already '
                      'running, it does not need its own drivers, filesystem code or network '
                      'stack, and hardware support is whatever the kernel supports. It '
                      'communicates with the firmware beneath it through NVRAM variables -- on '
                      'OpenPOWER, `petitboot,*` settings read and written through OPAL -- so '
                      'choices persist across reboots. Its own daemon and UI talk over a local '
                      'protocol, which is why the interface can be ncurses on a console or a '
                      'remote client.',
        handoff='The transfer is `kexec`: the target kernel and initrd are loaded into memory, '
                'the purgatory code verifies them, and the running kernel is replaced in place '
                'without a firmware reset. The device tree is passed through, so the new kernel '
                'sees the same machine description skiboot built.',
    ),
    'kexec-tools': Bootloader(
        summary='Userspace tooling to boot a new kernel from a running one.',
        boot_role='Loads a kernel image into memory and transfers control without firmware re- '
                  'init.',
        type_rationale='Type 2: an OS-loading stage that assumes a fully initialised machine.',
        target='New kernel',
        stages=(
            Stage('kexec -l',
                  "Loads a kernel, initrd and command line into the running kernel's memory "
                  'through the kexec_load syscall.',
                  'segments loaded via kexec_load'),
            Stage('segment placement',
                  'The kernel decides where the segments live, avoiding memory in use, and '
                  'records them for the reboot path.',
                  'placement map recorded'),
            Stage('purgatory',
                  'A small position-independent stub is placed between the two kernels; it '
                  'verifies segment checksums after the old kernel has stopped.',
                  'purgatory stub + checksums'),
            Stage('kexec -e',
                  'Devices are shut down, the CPU is put in a known state, and control jumps to '
                  'purgatory and then the new kernel.',
                  'boot_params or device tree'),
        ),
        communication='The whole point is to skip firmware, so nothing is re-discovered: the '
                      'new kernel is given its boot parameters and device tree or boot_params '
                      'structure directly by the old one, built in userspace by kexec-tools '
                      'from `/proc/iomem`, `/sys/firmware/fdt` and the existing command line. '
                      'The only code that runs between the two kernels is purgatory, which is '
                      'deliberately tiny because at that point there is no kernel to fall back '
                      'on. `kexec -p` reserves a separate region at boot for a crash kernel, so '
                      'a dump kernel can start from a machine that has already failed.',
        handoff="Control passes to the new kernel's normal entry point in the state the "
                "architecture's boot protocol specifies -- for x86 a filled-in `boot_params`, "
                'for ARM and Power a device tree pointer. Firmware is never re-entered, which '
                'is both the speed advantage and the limitation: hardware left in a bad state '
                'by the old kernel is not reset.',
    ),
    'u-root': Bootloader(
        summary='Go userspace and bootloader for LinuxBoot.',
        boot_role='Runs as an initramfs inside a Linux kernel embedded in firmware, then kexecs '
                  'the target kernel.',
        type_rationale='Type 2: the OS-facing half of a LinuxBoot image; the firmware beneath '
                       'it is Type 1.',
        target='Target OS kernel',
        stages=(
            Stage('initramfs start',
                  "The Linux kernel starts u-root's Go userland as PID 1 from an initramfs.",
                  'PID 1 in initramfs'),
            Stage('init and shell',
                  'Sets up /proc, /sys and /dev, then runs the u-root shell or a specified '
                  'uinit.',
                  '/proc, /sys, /dev ready'),
            Stage('boot policy',
                  'Commands such as `boot`, `fbnetboot` or `localboot` find boot targets on '
                  'disk or over the network.',
                  'discovered boot targets'),
            Stage('kexec',
                  "The selected kernel and initrd are loaded and kexec'd.",
                  'kexec: kernel + initrd + cmdline'),
        ),
        communication='u-root is a userland, so its interfaces are files and syscalls rather '
                      'than tables: it reads existing configurations (GRUB, syslinux, BLS '
                      'entries) from mounted filesystems, gets network configuration over DHCP, '
                      'and can verify what it found using TPM measurements or signatures before '
                      'acting on it. Because the boot policy is a Go program, an operator can '
                      'replace it entirely, which is the LinuxBoot argument -- driver and '
                      'policy code moves out of firmware and into a kernel and userland that '
                      'can be updated and audited normally.',
        handoff="The handoff is kexec into the target kernel. u-root's own kexec implementation "
                'builds the boot parameters and calls `kexec_file_load` where available, so '
                'signature verification can be done by the kernel rather than in userspace.',
    ),
    'linuxboot': Bootloader(
        summary='Replaces UEFI DXE with a Linux kernel and userspace.',
        boot_role='Keeps vendor PEI for silicon init, then runs Linux as the boot environment.',
        type_rationale='Type 2: it is the OS-loading stage layered on vendor Type 1 firmware.',
        target='Target OS kernel',
        stages=(
            Stage('vendor firmware PEI',
                  "The platform's existing UEFI firmware runs SEC and PEI to bring up memory.",
                  'DRAM up (vendor PEI)'),
            Stage('DXE replacement',
                  'Most of the DXE volume is removed and replaced with a Linux kernel and '
                  'initramfs.',
                  'kernel + initramfs spliced into flash'),
            Stage('Linux start',
                  'The kernel boots with the drivers the platform needs.',
                  'drivers loaded'),
            Stage('u-root policy',
                  'The u-root userland runs as init and decides what to boot.',
                  'boot policy decision'),
            Stage('kexec',
                  "The target OS kernel is loaded and kexec'd.",
                  'kexec: kernel + initrd'),
        ),
        communication="LinuxBoot is a firmware surgery project: it keeps the vendor's SEC and "
                      'PEI phases, because memory initialisation is board-specific and often '
                      'blob-bound, and replaces what comes after with Linux. The consequence '
                      'for communication is that the UEFI HOB and protocol machinery ends where '
                      "DXE would have started; from then on the interfaces are the kernel's -- "
                      'device tree or ACPI, sysfs, standard drivers. Tools in this repository '
                      'do the splicing on the flash image itself.',
        handoff='The final handoff is a kexec performed by u-root. Because the runtime services '
                'a normal UEFI machine would leave behind are largely gone, the OS is booted '
                'more like an embedded system than a PC, which is the trade LinuxBoot makes for '
                'a much smaller closed-source surface.',
    ),
    'syslinux': Bootloader(
        summary='SYSLINUX family: SYSLINUX, ISOLINUX, PXELINUX, EXTLINUX.',
        boot_role='Boots Linux from FAT, ISO9660, network or ext filesystems, driven by a '
                  'config file.',
        type_rationale='Type 2: configuration-driven OS loading from an initialised machine.',
        target='Kernel or chainloaded loader',
        stages=(
            Stage('first sector',
                  'SYSLINUX, EXTLINUX and ISOLINUX each install a small loader in the volume '
                  'boot record or boot image; PXELINUX is fetched over TFTP instead.',
                  'location of ldlinux.sys'),
            Stage('core (ldlinux.sys)',
                  'The core module is loaded next and provides file access, memory management '
                  'and the module loader.',
                  'file access + module loader'),
            Stage('configuration',
                  'syslinux.cfg (or a PXE-specific path derived from the MAC or IP) is read and '
                  'its LABEL entries become menu items.',
                  'LABEL entries and APPEND lines'),
            Stage('com32 modules',
                  'Modules such as menu.c32, vesamenu.c32 and chain.c32 extend the loader with '
                  'menus, chainloading and hardware probing.',
                  'menu selection via COM32 syscalls'),
            Stage('boot',
                  'The selected kernel is loaded, or another bootloader is chainloaded.',
                  'kernel + initrd + cmdline'),
        ),
        communication='Each SYSLINUX variant differs only in how it reads files -- FAT, ext, '
                      'ISO 9660, or TFTP -- and presents the same interface above that, which '
                      'is why one configuration format serves all four. Modules are COM32 '
                      'executables that call back into the core through a documented syscall '
                      'table, so a menu module can list files, read the configuration and then '
                      'load a kernel without linking against the core. PXELINUX additionally '
                      "keeps the DHCP packet available so scripts can key on the client's "
                      'identity.',
        handoff='For Linux it loads the kernel and initrd, builds the command line from the '
                "LABEL's APPEND line, and enters through the standard x86 boot protocol. "
                '`chain.c32` instead loads another boot sector -- the usual route to the '
                'Windows boot manager. MEMDISK is the unusual case: it loads a whole floppy or '
                'disk image into memory and hooks INT 0x13 so a legacy OS boots from what it '
                'believes is real hardware.',
    ),
    'bootboot': Bootloader(
        summary='Multi-architecture boot protocol and reference loaders.',
        boot_role='Provides a uniform machine state to the kernel across BIOS, UEFI and RPi.',
        type_rationale='Type 2: implements a protocol for handing off to an OS kernel.',
        target='Kernel<br/>(ELF or PE)',
        stages=(
            Stage('platform loader',
                  'A per-platform first stage -- BIOS, UEFI application, coreboot payload or '
                  'Raspberry Pi start.elf -- loads the BOOTBOOT image.',
                  'BOOTBOOT image loaded'),
            Stage('environment parse',
                  'Reads BOOTBOOT/CONFIG, a plain text key-value file on the boot partition.',
                  'environment string from CONFIG'),
            Stage('initrd load',
                  'Locates the initial ramdisk and finds the kernel inside it (ELF or PE, at a '
                  'fixed path).',
                  'initrd + kernel located'),
            Stage('mapping',
                  'Sets up long mode, identity and higher-half mappings, and the framebuffer.',
                  'long mode, higher-half map, framebuffer'),
            Stage('kernel entry',
                  'Enters the kernel on all cores with a defined environment.',
                  'BOOTBOOT struct at a fixed address'),
        ),
        communication='BOOTBOOT is a protocol first and an implementation second: its contract '
                      'is a single `BOOTBOOT` structure at a fixed virtual address, describing '
                      'the memory map, framebuffer, initrd location, SMP core count and the '
                      'real-time clock, alongside the environment string parsed from CONFIG. '
                      'Because every platform implementation produces the same structure, a '
                      'kernel written against it boots unchanged on BIOS, UEFI, coreboot and '
                      'Raspberry Pi -- the differences are absorbed by the loader.',
        handoff='The kernel is entered in 64-bit mode with paging already configured and the '
                'same static addresses on every core, so it does not have to parse anything or '
                'bring up SMP itself. This is deliberately more prepared a handoff than '
                "Multiboot's, and it is the reason BOOTBOOT is aimed at hobby kernels.",
    ),
    'OpenCorePkg': Bootloader(
        summary='OpenCore, a UEFI bootloader for running macOS on unsupported hardware.',
        boot_role='Injects ACPI, kext and SMBIOS patches, then boots macOS, Windows or Linux.',
        type_rationale='Type 2: a UEFI application that prepares and launches an OS.',
        target='macOS<br/>(via boot.efi)',
        stages=(
            Stage('loaded by firmware',
                  'OpenCore.efi is loaded from the ESP as a UEFI application, or chainloaded '
                  'from another loader.',
                  'image handle + system table'),
            Stage('config.plist parse',
                  'A single property list drives everything: ACPI patches, kernel extensions, '
                  'device properties, quirks and the boot picker.',
                  'quirks, patches and device properties'),
            Stage('ACPI and SMBIOS patching',
                  'Tables are added, dropped or patched before the OS sees them, and SMBIOS is '
                  'rewritten to match a supported Mac model.',
                  'patched ACPI + faked SMBIOS'),
            Stage('driver injection',
                  'UEFI drivers are loaded for filesystems (APFS, HFS+) and missing firmware '
                  'features.',
                  'injected drivers and kexts'),
            Stage('kernel or loader start',
                  'boot.efi is started for macOS, with kext injection and kernel patches '
                  'applied on the way, or another OS is chainloaded.',
                  'prepared UEFI environment'),
        ),
        communication="OpenCore's job is to make a non-Apple machine present the environment "
                      'macOS expects, so almost all of its communication is interception: it '
                      'patches the ACPI tables and SMBIOS the firmware built, injects device '
                      'properties into the tree, and applies binary patches to the kernel and '
                      'to kexts as they are loaded. NVRAM is the other channel -- `boot-args`, '
                      'the boot device path and Apple-specific variables are written there, and '
                      'OpenCore can emulate NVRAM on firmware that does not persist it '
                      'properly.',
        handoff="For macOS, control goes to Apple's own `boot.efi`, which OpenCore has already "
                'prepared the environment for; boot.efi then starts the kernel. For Windows or '
                'Linux it is an ordinary UEFI chainload. Because the patches are applied in '
                'memory rather than on disk, the installed OS is unmodified -- which is what '
                'makes updates survivable.',
    ),
    'CloverBootloader': Bootloader(
        summary='Clover, an earlier macOS-focused UEFI bootloader.',
        boot_role='Similar role to OpenCore, with its own patching model.',
        type_rationale='Type 2: a UEFI application that launches an OS.',
        target='macOS<br/>(via boot.efi)',
        stages=(
            Stage('CloverEFI or native UEFI',
                  'On legacy BIOS machines CloverEFI provides a UEFI emulation layer first; on '
                  'UEFI machines CLOVERX64.efi is loaded directly.',
                  'UEFI environment (real or emulated)'),
            Stage('config.plist parse',
                  'Configuration for patches, SMBIOS, devices and the GUI is read from a '
                  'property list.',
                  'config.plist settings'),
            Stage('table patching',
                  'ACPI is patched (DSDT fixes, SSDT injection) and SMBIOS is rewritten.',
                  'patched DSDT/SSDT + SMBIOS'),
            Stage('GUI',
                  'A themed boot picker scans volumes and lists the operating systems it '
                  'recognises.',
                  'user selection'),
            Stage('start',
                  'boot.efi is launched for macOS, or another loader is chainloaded.',
                  'prepared UEFI environment'),
        ),
        communication='Clover predates OpenCore and takes a broader approach: as well as '
                      'patching tables and injecting drivers, it can supply the UEFI '
                      'environment itself on machines that have none, which is why the tree '
                      'carries a large slice of EDK II. Configuration and the same interception '
                      'channels -- ACPI, SMBIOS, NVRAM, device properties -- are the mechanism, '
                      "with more automatic fixups applied by default than OpenCore's "
                      'explicitly-listed quirks.',
        handoff="As with OpenCore, macOS is reached through Apple's `boot.efi` and other "
                'systems through a UEFI chainload. The wider surface is the trade: more is '
                "patched on the machine's behalf, and more of the firmware environment is "
                "Clover's own code rather than the platform's.",
    ),
    'chameleon': Bootloader(
        summary='Legacy Darwin/x86 boot loader.',
        boot_role='BIOS-era loader for booting macOS on generic hardware.',
        type_rationale='Type 2: it loads an OS from an initialised BIOS machine.',
        target='XNU kernel',
        stages=(
            Stage('boot0',
                  'MBR code that finds the active partition and loads boot1.',
                  'active partition located'),
            Stage('boot1',
                  'Partition boot sector code that locates the boot file in the filesystem.',
                  'boot file found in filesystem'),
            Stage('boot2',
                  'The bootloader proper: reads configuration, patches tables, presents a '
                  'device picker.',
                  'org.chameleon.Boot.plist applied'),
            Stage('kernel load',
                  'Loads the XNU kernel and mkext/kext caches, applies patches, and enters the '
                  'kernel.',
                  'boot-args + constructed device tree'),
        ),
        communication="Chameleon descends from Apple's open-source boot-132 and works entirely "
                      'in the legacy BIOS world, so its stage boundaries are the classic '
                      'sector-size ones and its services come from BIOS interrupts. '
                      'Configuration is `org.chameleon.Boot.plist`, and injection is done by '
                      'building the ACPI tables, SMBIOS and device properties in memory before '
                      'XNU is started. It is effectively superseded by Clover and OpenCore, '
                      'which is why it appears here mainly as the earlier generation of the '
                      'same idea.',
        handoff='The XNU kernel is entered directly with a boot-args structure describing '
                'memory, the framebuffer and the kernel command line, together with the device '
                'tree Chameleon constructed. Unlike the UEFI-era loaders there is no `boot.efi` '
                'in the chain.',
    ),
    'tboot-mirror': Bootloader(
        summary='Trusted Boot, a pre-kernel module for Intel TXT measured launch.',
        boot_role='Performs a measured launch of the kernel or hypervisor using TXT and the '
                  'TPM.',
        type_rationale='Type 2: it sits between firmware and the OS, measuring and launching '
                       'it.',
        target='Kernel or VMM<br/>(measured)',
        stages=(
            Stage('loaded by GRUB',
                  'tboot is loaded as a Multiboot module ahead of the kernel or hypervisor it '
                  'will measure.',
                  'Multiboot modules + tboot'),
            Stage('pre-launch checks',
                  'Verifies TXT capability, the chipset, and that the SINIT ACM matches the '
                  'platform.',
                  'TXT capability confirmed'),
            Stage('GETSEC[SENTER]',
                  'Executes the measured launch: the CPU and chipset reset the dynamic PCRs, '
                  'the ACM is verified by microcode, and it measures the MLE.',
                  'dynamic PCRs 17-22 extended'),
            Stage('policy evaluation',
                  'The launch control policy and verified launch policy are checked against '
                  'measurements of the kernel and its modules.',
                  'policy satisfied'),
            Stage('kernel start',
                  'If policy is satisfied, the kernel or VMM is started in the measured '
                  'environment.',
                  'txt_info + TXT heap, DMA protected'),
        ),
        communication="tboot's communication is with the TPM rather than with the next stage. "
                      'The dynamic PCRs (17-22) are reset by the SENTER instruction and '
                      'extended with measurements of the ACM, tboot itself, and each module it '
                      'was given; policies are stored in TPM NVRAM so they cannot be swapped '
                      'along with the disk image. What tboot passes forward to the OS is a '
                      '`txt_info` structure and the TXT heap, telling the kernel it was '
                      'launched measured and where the protected regions are.',
        handoff='Control reaches the kernel or hypervisor through the normal Multiboot handoff, '
                'but in a machine state SENTER established: DMA protection is in place for the '
                'measured regions and the dynamic root of trust has been recorded. A later '
                'attestation verifies the PCR values rather than trusting the boot chain to '
                'have been honest.',
    ),
    'aboot': Bootloader(
        summary='Android bootloader (the historical Alpha aboot in this corpus).',
        boot_role='Loads and verifies an Android boot image.',
        type_rationale='Type 2: an OS-loading stage.',
        target='Linux kernel<br/>(Alpha)',
        stages=(
            Stage('SRM console',
                  "Alpha's SRM firmware initialises the machine and reads the bootstrap blocks "
                  'from the boot device.',
                  'SRM callback interface'),
            Stage('bootstrap loader',
                  'The bootblock loads aboot itself from the reserved area at the start of the '
                  'disk.',
                  'aboot loaded from bootblocks'),
            Stage('filesystem access',
                  'aboot reads ext2, ISO 9660 or UFS directly to find the kernel.',
                  'kernel located in filesystem'),
            Stage('kernel load',
                  'Loads the kernel, resolves arguments from /etc/aboot.conf, and starts it.',
                  'kernel + cmdline from aboot.conf'),
        ),
        communication="aboot sits on SRM's callback interface: the firmware stays available for "
                      'console and disk access, so aboot does not need its own drivers for the '
                      'boot path. Its own configuration is `/etc/aboot.conf`, read from the '
                      'target filesystem, where numbered entries map a short selection made at '
                      'the SRM prompt onto a full kernel path and command line. This is the '
                      'Alpha equivalent of the arrangement the paper describes for BIOS-era '
                      'loaders -- firmware services remain callable across the boundary.',
        handoff='The kernel is entered with its command line and, where used, an initial '
                'ramdisk. It is a historical loader, included in the corpus as an example of a '
                'non-x86, non-ARM boot path built on a firmware callback interface rather than '
                'on tables.',
    ),
    'quibble': Bootloader(
        summary='Open-source Windows boot loader replacement.',
        boot_role='Loads the Windows kernel from a filesystem GRUB can reach.',
        type_rationale='Type 2: it prepares and launches an OS.',
        target='Windows kernel<br/>(ntoskrnl.exe)',
        stages=(
            Stage('loaded by firmware',
                  'quibble.efi is loaded from the ESP in place of bootmgfw.efi.',
                  'image handle + system table'),
            Stage('registry read',
                  'Reads the SYSTEM hive to find the boot-start drivers and the services the '
                  'kernel needs.',
                  'boot-start driver list'),
            Stage('filesystem drivers',
                  'Loads its own drivers -- Btrfs, ext, NTFS -- so Windows can be booted from '
                  'filesystems the official loader does not support.',
                  'readable non-NTFS volumes'),
            Stage('image loading',
                  'Loads the kernel, HAL and boot drivers, relocating and linking them as the '
                  'loader is required to.',
                  'relocated kernel, HAL and drivers'),
            Stage('kernel start',
                  'Builds the loader block and enters the kernel.',
                  'LOADER_PARAMETER_BLOCK'),
        ),
        communication='Quibble is a reimplementation of `bootmgfw.efi` and `winload.efi`, so '
                      'the interface it must reproduce is the LOADER_PARAMETER_BLOCK: a large '
                      'structure describing loaded modules, memory descriptors, the ARC device '
                      'paths, registry data and the boot options the kernel expects to find. '
                      'That structure changed across Windows versions, which is most of the '
                      'difficulty -- the correct layout has to be produced for anything from XP '
                      'to Windows 10 22H2. Boot configuration otherwise comes from the SYSTEM '
                      'hive rather than from BCD.',
        handoff='Control passes to `ntoskrnl.exe` at its entry point with a pointer to the '
                'loader block, in the same state the Microsoft loader would have left. The '
                'project is explicitly a proof of concept, and its interest in this corpus is '
                'as an independent implementation of a closed handoff protocol.',
    ),
    'easyboot': Bootloader(
        summary='Multi-kernel boot manager built on the BOOTBOOT protocol.',
        boot_role='Presents a menu and boots kernels in several formats.',
        type_rationale='Type 2: OS selection and launch.',
        target='Kernel<br/>(Multiboot2 or native)',
        stages=(
            Stage('platform stage',
                  'A BIOS, UEFI, coreboot or Raspberry Pi first stage loads the Easyboot image.',
                  'Easyboot image loaded'),
            Stage('menu configuration',
                  'Reads a simple plain-text menu file from the boot partition.',
                  'parsed menu entries'),
            Stage('kernel selection',
                  'Presents entries and loads the chosen kernel, in ELF, PE or a.out form.',
                  'kernel image in memory'),
            Stage('protocol handoff',
                  "Boots it with Multiboot2 or the kernel's own expected protocol.",
                  'Multiboot2 information tag list'),
        ),
        communication='Easyboot is a boot manager built around the idea that the configuration '
                      'should be readable and the loader should not need plugins: filesystem '
                      'and format support are compiled in, and a single text file describes the '
                      'menu. Where a kernel asks for Multiboot2 it receives the standard '
                      'information tag list -- memory map, module list, framebuffer, ACPI '
                      "pointers -- which is the mechanism the paper describes for GRUB's "
                      'Multiboot path.',
        handoff='The kernel is entered with the Multiboot2 information structure in the '
                'register the specification defines, or, for kernels that ask for it, in the '
                'simpler arrangement its smaller sibling Simpleboot uses. Like BOOTBOOT, from '
                'the same author, its goal is that one loader image works across firmware types '
                'without the kernel noticing.',
    ),
    'tosaithe': Bootloader(
        summary='Minimal UEFI boot menu and Stivale2 loader.',
        boot_role='Boots hobby-OS kernels from UEFI.',
        type_rationale='Type 2: a UEFI application that loads a kernel.',
        target='Kernel<br/>(TSBP · Linux · chainload)',
        stages=(
            Stage('loaded by firmware',
                  'A UEFI application started from the ESP.',
                  'image handle + system table'),
            Stage('configuration',
                  'Reads its menu configuration and presents entries.',
                  'menu entries'),
            Stage('image load',
                  'Loads a Linux kernel, chainloads another EFI program, or loads a TSBP '
                  'kernel.',
                  'kernel in memory'),
            Stage('handoff',
                  'Enters the kernel according to the protocol it uses.',
                  'TSBP struct, paging on'),
        ),
        communication='Tosaithe is small and UEFI-only by design, and exists mainly as the '
                      'reference implementation of the Tosaithe Boot Protocol. Under TSBP the '
                      'loader passes a single structure describing the memory map, framebuffer, '
                      "ACPI and the loaded kernel's own segments, with the page tables already "
                      "established -- the same philosophy as Limine's, with a smaller surface.",
        handoff='For a TSBP kernel it enters 64-bit mode with mappings in place and the '
                'information structure in a defined register, after calling '
                '`ExitBootServices()`. For Linux it uses the EFI stub path, and for a chainload '
                'it simply starts another EFI image.',
    ),
    'x86-bootloader': Bootloader(
        summary='Teaching-scale x86 bootloader.',
        boot_role='A minimal MBR loader demonstrating the real-mode to protected-mode '
                  'transition.',
        type_rationale='Type 2: it starts after BIOS and loads a kernel.',
        target='Kernel<br/>(C, 32-bit)',
        stages=(
            Stage('boot sector',
                  '512 bytes loaded by BIOS to 0x7C00, ending in the 0xAA55 signature.',
                  '512 bytes at 0x7C00'),
            Stage('disk read',
                  'Uses INT 0x13 to read the rest of the loader and the kernel off the disk.',
                  'loader + kernel in memory'),
            Stage('GDT and A20',
                  'Sets up a flat global descriptor table and enables the A20 line.',
                  'flat GDT, A20 enabled'),
            Stage('protected mode',
                  'Sets the PE bit in CR0 and far-jumps to flush the pipeline into 32-bit code.',
                  '32-bit protected mode'),
            Stage('kernel entry',
                  'Calls into the C kernel it loaded.',
                  'direct call at a fixed address'),
        ),
        communication='This is a teaching implementation, so the mechanisms are the bare ones: '
                      'BIOS interrupts for disk and screen while still in real mode, and fixed '
                      'load addresses agreed between the assembly stub and the linker script. '
                      'There is no configuration file and no negotiated structure -- the '
                      'contract between stages is the memory map written in the source.',
        handoff='The kernel is entered by a direct call once protected mode is on. Its value in '
                'this corpus is that the whole Type 2 skeleton -- sector load, mode switch, '
                'jump -- is small enough to read in one sitting, which makes it useful for '
                'teaching the shape that the production loaders elaborate on.',
    ),
    'bootloader': Bootloader(
        summary='rust-osdev/bootloader, a Rust x86_64 kernel loader.',
        boot_role='Loads a Rust kernel from BIOS or UEFI and sets up paging before handoff.',
        type_rationale='Type 2: it starts from an initialised platform and prepares a kernel.',
        target='Rust kernel',
        stages=(
            Stage('BIOS or UEFI first stage',
                  'On BIOS a 512-byte stage loads stage 2 and stage 3, which switch to '
                  'protected then long mode; on UEFI the firmware loads the bootloader '
                  'directly.',
                  'long mode, stage 3 loaded'),
            Stage('common stage',
                  'Shared Rust code takes over: it reads the kernel ELF from the disk image.',
                  'kernel ELF parsed'),
            Stage('paging setup',
                  'Builds page tables, maps the kernel, and optionally maps all physical memory '
                  'at a configurable offset.',
                  'page tables + physical memory map'),
            Stage('boot info assembly',
                  'Fills in a BootInfo struct with the memory map, framebuffer, physical memory '
                  'offset and ACPI pointer.',
                  'BootInfo populated'),
            Stage('kernel entry',
                  'Jumps to the kernel entry point with a reference to BootInfo.',
                  "&'static mut BootInfo"),
        ),
        communication='The interesting property is that the handoff is typed. The bootloader '
                      'and the kernel are both Rust crates that share the `bootloader_api` '
                      'crate, so the `BootInfo` structure the loader fills in is the same '
                      'definition the kernel destructures -- an ABI mismatch becomes a compile '
                      'error rather than a corrupted pointer. Configuration is done at build '
                      "time through the API's `BootloaderConfig`, not through a file read at "
                      'boot.',
        handoff='The kernel is entered in long mode with its page tables installed and a '
                "`&'static mut BootInfo` as its argument. On UEFI, `ExitBootServices()` has "
                'already been called and the memory map captured into that structure.',
    ),
    'MiniVisorPkg': Bootloader(
        summary='Minimal research hypervisor loadable from UEFI.',
        boot_role='Installs a thin hypervisor before the OS boots.',
        type_rationale='Type 2: a UEFI-loaded stage that runs before and hands off to an OS.',
        target='Firmware<br/>(now running as guest)',
        stages=(
            Stage('UEFI driver load',
                  'MiniVisor is loaded as a UEFI driver, typically from the UEFI shell, before '
                  'any OS starts.',
                  'image handle + system table'),
            Stage('VMX setup',
                  'Enables VMX operation, allocates VMCS and EPT structures for each processor.',
                  'VMCS + EPT per processor'),
            Stage('virtualisation of the running context',
                  'The currently executing environment -- the firmware -- becomes the guest, '
                  'with the hypervisor beneath it.',
                  'VM-exit interface'),
            Stage('boot continues',
                  'The firmware and then the OS continue running as a guest, observed by the '
                  'hypervisor.',
                  'control returned, boot continues'),
        ),
        communication='This is not a bootloader in the sense of loading anything; it is in the '
                      'corpus because it occupies the boot path. Its communication with what '
                      "runs above it is the VM-exit interface: the guest's privileged "
                      'operations trap into the hypervisor, which logs or modifies them. As a '
                      'Windows driver build it uses the same core with a different loader, so '
                      'the same code can be debugged with WinDbg.',
        handoff='There is no handoff -- control returns to the firmware, which proceeds to the '
                'real boot. The relevance to bootloader security is that code installed this '
                'early sits underneath everything the OS can inspect, which is precisely the '
                'position a bootkit wants.',
    ),
    'open-iscsi': Bootloader(
        summary='Linux iSCSI initiator, used for network root and boot.',
        boot_role='Establishes iSCSI sessions so a remote volume can serve as the boot disk.',
        type_rationale='Type 2 by association: it is boot-path infrastructure for network boot '
                       'rather than a bootloader that transfers control to a kernel. The '
                       'weakest fit in the corpus.',
        target='Root filesystem<br/>(remote volume)',
        stages=(
            Stage('firmware or iBFT stage',
                  "A network card's option ROM or the firmware establishes the initial iSCSI "
                  'session and records the parameters in the iSCSI Boot Firmware Table.',
                  'iBFT in ACPI: target, LUN, CHAP'),
            Stage('initramfs start',
                  'Linux boots far enough to run an initramfs containing iscsistart.',
                  'iscsistart in initramfs'),
            Stage('session re-establishment',
                  'The iBFT parameters are read from /sys/firmware/ibft and the session is re- '
                  'created by the in-kernel initiator.',
                  'kernel-owned session'),
            Stage('root mount',
                  'The remote volume appears as a SCSI disk and the root filesystem is mounted '
                  'from it.',
                  'SCSI disk ready to mount'),
        ),
        communication='open-iscsi is boot-path infrastructure rather than a bootloader, and the '
                      'handoff it participates in is a state transfer: the firmware-owned '
                      'session must be replaced by a kernel-owned one without the block device '
                      'disappearing underneath the mount. iBFT is the structure that makes that '
                      'possible -- the firmware publishes target address, LUN, initiator name '
                      'and CHAP credentials in an ACPI table, and the initramfs reads them back '
                      'out.',
        handoff='There is no transfer of control to a next stage. It is included because the '
                'corpus tracks the boot path as an attack surface, and a root filesystem '
                'reached over the network -- with credentials sitting in an ACPI table -- is '
                'part of that path.',
    ),
    # ---- Type 3: monolithic bootloaders -----------------------------------
    'u-boot': Bootloader(
        summary='Das U-Boot, the dominant embedded bootloader.',
        boot_role='SPL performs DRAM and clock init from reset, then full U-Boot loads a '
                  'kernel, device tree and initrd, with a command shell and scripting '
                  'throughout.',
        type_rationale='Type 3: SPL plus U-Boot together take the board from reset to a running '
                       'OS with no separate firmware layer -- one project spans both roles.',
        case_study='3.7',
        target='Operating system<br/>(Linux · EFI application)',
        stages=(
            Stage('SoC ROM code',
                  'OEM code in mask ROM runs from the reset vector and does the minimum needed '
                  'to load the next image, often from a fixed offset on eMMC or SPI flash.',
                  'next image from a fixed flash offset'),
            Stage('TPL',
                  'Optional tertiary program loader: very early hardware setup, used where the '
                  'ROM can only load a very small image. Loads SPL or VPL.',
                  'early hardware up'),
            Stage('VPL',
                  'Optional verification program loader, which selects among multiple verified '
                  'SPL binaries.',
                  'chosen SPL binary'),
            Stage('SPL',
                  'Secondary program loader. Initialises DRAM and loads full U-Boot into it -- '
                  'or, in Falcon mode, loads the Linux kernel directly and skips the rest.',
                  'DRAM up, spl_image_info + bloblist'),
            Stage('U-Boot proper',
                  'The full image: driver model, filesystems, network stack, environment and '
                  'the command shell.',
                  'drivers, env, shell ready'),
            Stage('bootdev',
                  'Abstracts the device that may hold an OS -- MMC, USB, NVMe, network.',
                  'candidate boot devices'),
            Stage('bootmeth',
                  'Defines how each bootdev is searched for a valid boot configuration -- '
                  'extlinux.conf, an EFI application, a script.',
                  'located boot configuration'),
            Stage('bootflow',
                  'The concrete sequence produced by a bootmeth on a bootdev. The first valid '
                  'one found is used by default.',
                  'kernel + initrd + fixed-up FDT'),
        ),
        communication='Because the stages are separate images built from one tree, U-Boot '
                      'passes state forward explicitly: SPL hands U-Boot a `struct '
                      'spl_image_info`, and where the same information must survive from before '
                      'DRAM exists it travels in a bloblist -- a relocatable container that '
                      'also carries ACPI tables, the device tree and SMBIOS data between '
                      'stages. The persistent interface is the environment: a key-value store '
                      'in flash (`bootargs`, `bootcmd`, `fdt_addr`) readable and writable from '
                      'the shell and by scripts, which is how a bootflow is altered without '
                      'rebuilding. U-Boot can also present itself as UEFI, publishing Boot and '
                      'Runtime Services so a standard distribution loader runs unmodified.',
        handoff="The OS is started with the architecture's boot protocol, and the important "
                'thing passed is the flattened device tree: U-Boot may fix it up first -- '
                'inserting the MAC address, memory size, or kernel command line -- so the '
                'kernel sees a description matched to the actual board. An extlinux.conf-driven '
                'bootflow supplies the kernel, the command line, the device tree directory and '
                "the initrd, as in the paper's Listing 2. Changing anything more than the "
                'bootflow generally means reflashing.',
    ),
    'barebox': Bootloader(
        summary='U-Boot alternative with a Linux-like driver model.',
        boot_role='Initialises the board from reset and boots a kernel, with a shell and a '
                  'filesystem-like device model.',
        type_rationale='Type 3: hardware bring-up and OS launch in one image.',
        target='Operating system',
        stages=(
            Stage('PBL (pre-bootloader)',
                  'A small compressed prologue that runs from SRAM, sets up DRAM, and '
                  'decompresses barebox proper into it.',
                  'DRAM up, barebox decompressed'),
            Stage('barebox proper',
                  'Full initialisation: driver model, filesystem layer, network stack, and the '
                  'shell.',
                  'drivers, filesystems, env'),
            Stage('bootentry discovery',
                  'Boot entries are collected from bootloader spec files, scripts in /env/boot, '
                  'or the device tree.',
                  'bootentries + bootchooser slot'),
            Stage('boot',
                  'The chosen entry loads a kernel, device tree and initrd, and starts it.',
                  'kernel + initrd + FDT'),
        ),
        communication="barebox follows U-Boot's role but borrows the kernel's design: a POSIX- "
                      'like filesystem layer where devices, variables and configuration all '
                      'appear as files, so a boot script manipulates `/env/` and `/dev/` with '
                      'ordinary shell commands. State the PBL gathers before DRAM exists is '
                      'passed to the main image in handoff data. The state that matters most '
                      "across reboots is the bootchooser's: per-slot priority and remaining- "
                      'attempts counters, stored in persistent storage and decremented on each '
                      'try, so a failed update rolls back automatically.',
        handoff='The kernel is entered with the device tree barebox assembled and fixed up, '
                'following the same ARM/RISC-V protocol U-Boot uses. barebox also implements '
                'enough of UEFI to start an EFI stub kernel, and can run as an EFI application '
                'itself.',
    ),
    'mcuboot': Bootloader(
        summary='Secure bootloader for 32-bit microcontrollers.',
        boot_role='Validates image signatures, manages primary/secondary slots, handles '
                  'rollback and swap, then jumps to the application.',
        type_rationale='Type 3: it runs from reset on the MCU and jumps straight into the '
                       'application -- there is no OS-loader stage to hand off to.',
        case_study='3.6',
        target='Application<br/>(Zephyr · Mynewt · NuttX)',
        stages=(
            Stage('reset vector',
                  'The MCU resets into MCUboot, which occupies the first region of flash.',
                  'reset handler entered'),
            Stage('bootutil',
                  'The core library: reads the image headers and TLV trailers, validates '
                  'signatures and hashes, and implements the swap logic.',
                  'headers and TLV trailers parsed'),
            Stage('slot selection',
                  "Decides between the primary and secondary slot based on the image trailer's "
                  'flags -- a pending update, a test image awaiting confirmation, or a revert.',
                  'chosen slot (primary or secondary)'),
            Stage('swap or overwrite',
                  'If an update is pending, the slots are swapped through the scratch area, or '
                  'the secondary simply overwrites the primary.',
                  'primary slot holds the valid image'),
            Stage('boot application',
                  'Board- and RTOS-specific code sets the vector table and stack pointer and '
                  "jumps to the primary slot's entry point.",
                  'vector table + SP set, branch'),
        ),
        communication="MCUboot's stage communication is flash layout. The image trailer at the "
                      'end of each slot holds the magic value, the image-OK and copy-done flags '
                      'and the swap status -- written in a defined order so an interrupted swap '
                      'can be resumed rather than bricking the device. That trailer is the only '
                      'channel between the running application and the bootloader: the '
                      'application confirms a new image by writing image-OK, and a reset '
                      'without that confirmation causes a revert. There are no system tables '
                      'and no runtime services; everything else is fixed at build time.',
        handoff='The jump to the application is deliberately minimal -- vector table relocated, '
                'stack pointer set, branch to the reset handler -- and nothing is passed. The '
                'application can read boot metadata back through `boot_serial` or the shared '
                'data region if the platform enables it, which is also how measured-boot data '
                'reaches a TF-M secure image.',
    ),
    'arm-trusted-firmware': Bootloader(
        summary='Trusted Firmware-A, the Arm secure-world reference.',
        boot_role='BL1/BL2/BL31 bring the SoC up from reset, set up EL3 runtime services, then '
                  'enter the normal-world bootloader or OS.',
        type_rationale='Type 3 in this corpus: it spans reset to OS handoff. Arguably Type 1 in '
                       'a staged setup where BL33 is U-Boot.',
        target='Non-secure world<br/>(U-Boot · EDK II · kernel)',
        stages=(
            Stage('BL1',
                  'Runs from ROM at reset in EL3. Sets up the exception vectors and minimal '
                  'platform state, then loads and authenticates BL2.',
                  'authenticated BL2'),
            Stage('BL2',
                  'Trusted boot firmware. Initialises DRAM, then loads and authenticates every '
                  'image that follows: BL31, BL32 and BL33.',
                  'entry_point_info for BL31/32/33'),
            Stage('BL31',
                  'The EL3 runtime firmware. Installs the SMC handler, PSCI implementation and '
                  'interrupt routing, and stays resident for the life of the system.',
                  'SMC handler + PSCI resident at EL3'),
            Stage('BL32',
                  'Optional secure-world payload -- OP-TEE, TF-M or another trusted OS -- '
                  'running in S-EL1.',
                  'secure services at S-EL1'),
            Stage('BL33',
                  'The non-secure bootloader: U-Boot, EDK II or a kernel, entered in EL2 or '
                  'EL1.',
                  'eret into EL2/EL1'),
        ),
        communication='Images are described to each other by `entry_point_info` and '
                      "`image_info` structures that BL2 fills in and passes through BL31's "
                      'initialisation -- that is how BL31 knows where BL32 and BL33 should '
                      'start and in which exception level. Authentication is driven by a chain '
                      'of trust expressed as certificates in the FIP (Firmware Image Package), '
                      'so each stage verifies the next against keys rooted in the ROTPK held in '
                      'OTP. After boot, the interface is the SMC calling convention: PSCI calls '
                      'for CPU power management, and SMCs into the trusted OS.',
        handoff='BL31 does not hand control away and disappear. It `eret`s into BL33 at the '
                'exception level configured for it, and remains at EL3 to service SMCs -- so '
                'the normal-world bootloader and later the OS keep calling back into it for '
                'CPU_ON, system reset and secure services. This is why TF-A behaves as both a '
                'boot stage and a runtime component.',
    ),
    'trusted-firmware-m': Bootloader(
        summary='Trusted Firmware-M, the Armv8-M secure runtime.',
        boot_role='Secure boot (often MCUboot-based BL2) plus the secure processing environment '
                  'the non-secure application calls into.',
        type_rationale='Type 3: reset to application on a microcontroller.',
        target='Non-secure application',
        stages=(
            Stage('BL1',
                  'Optional immutable ROM stage on platforms that need one; verifies and loads '
                  'BL2.',
                  'verified BL2'),
            Stage('BL2 (MCUboot)',
                  'TF-M uses MCUboot as its second-stage loader to verify and, if needed, swap '
                  'the secure and non-secure images.',
                  'verified images + measurements'),
            Stage('SPE initialisation',
                  'The Secure Processing Environment sets up the SAU/IDAU and MPU so secure '
                  'memory and peripherals are unreachable from the non-secure side.',
                  'SAU/IDAU and MPU configured'),
            Stage('secure partitions',
                  'The partition manager starts the PSA RoT services -- Crypto, Internal '
                  'Trusted Storage, Protected Storage, Initial Attestation.',
                  'PSA RoT services + NSC veneers'),
            Stage('NSPE jump',
                  'Control is transferred to the non-secure application through a non-secure '
                  'function call.',
                  'BLXNS: NS stack pointer + vector table'),
        ),
        communication='The boundary here is spatial rather than temporal: after the jump, both '
                      'sides are running, and the interface between them is the Armv8-M '
                      'security extension. The non-secure application calls secure services '
                      'through veneer functions in the Non-Secure Callable region, which the '
                      'PSA Firmware Framework routes to the right partition. Measurements taken '
                      'by BL2 are passed up in a shared data region so the attestation service '
                      'can report what was actually loaded.',
        handoff='The transfer to the non-secure world sets the non-secure stack pointer and '
                'vector table from the NSPE image header and branches with `BLXNS`. Secure '
                'state is not torn down -- it stays resident for the life of the device, which '
                'is the whole point of the design.',
    ),
    'wolfBoot': Bootloader(
        summary='Portable secure bootloader from wolfSSL.',
        boot_role='Verifies firmware signatures with wolfCrypt, supports rollback protection '
                  'and encrypted updates, then boots the application.',
        type_rationale='Type 3: MCU-class reset-to-application boot.',
        target='Application<br/>(firmware or Linux)',
        stages=(
            Stage('stage1',
                  'On platforms that need it, a minimal first stage loads wolfBoot itself from '
                  'flash into RAM.',
                  'wolfBoot in RAM'),
            Stage('wolfBoot start',
                  'Minimal HAL initialisation -- clock, flash access -- and nothing more.',
                  'flash + clock access'),
            Stage('image verification',
                  'Parses the image header, checks the SHA digest and verifies the signature '
                  'with wolfCrypt, against a public key compiled into the bootloader.',
                  'signature verified by wolfCrypt'),
            Stage('update or rollback',
                  'If the update partition holds a newer verified image, the partitions are '
                  'swapped through the sector-based swap area; a failed confirmation triggers '
                  'rollback.',
                  'confirmed image in the boot partition'),
            Stage('application jump',
                  'Sets the vector table and jumps to the verified image.',
                  'vector table set, branch (PCRs extended)'),
        ),
        communication='wolfBoot follows RFC 9019, and its state is the partition trailer: '
                      'magic, partition state (`NEW`, `UPDATING`, `TESTING`, `SUCCESS`) and the '
                      'sector flags recording swap progress, so an interrupted update resumes. '
                      'Version monotonicity is enforced from the signed header, optionally '
                      'anchored in a TPM or in one-time-programmable memory to make rollback '
                      'impossible rather than merely discouraged. A running application signals '
                      'success by writing the trailer through the same API.',
        handoff='The jump to the application passes nothing beyond the hardware state. On '
                'platforms with a TPM, measurements are extended into PCRs first, so the '
                'application can attest to what booted it. wolfBoot can also chain into Linux '
                'on larger targets, where it fills the role a Type 1 stage would otherwise '
                'have.',
    ),
    'rustBoot': Bootloader(
        summary='Secure bootloader for MCUs written in Rust.',
        boot_role='Signature verification and A/B updates before jumping to the application.',
        type_rationale='Type 3: reset to application.',
        target='Firmware or Linux kernel',
        stages=(
            Stage('reset',
                  'The MCU or SoC resets into rustBoot, written entirely in Rust.',
                  'reset handler entered'),
            Stage('partition parse',
                  'Reads the boot and update partition headers and their trailers.',
                  'partition headers + trailers'),
            Stage('verification',
                  'Checks the image digest and verifies its ECC signature using RustCrypto.',
                  'ECC signature verified'),
            Stage('swap or boot',
                  'Swaps partitions if an update is pending and confirmed-valid; otherwise '
                  'boots the existing image.',
                  'valid image in the boot partition'),
            Stage('handoff',
                  'Jumps to the firmware image, or on Cortex-A loads and boots a Linux kernel.',
                  'branch, or kernel + FDT'),
        ),
        communication='rustBoot uses the same multi-slot, trailer-driven state machine the C '
                      'secure bootloaders use -- boot and update partitions, a state byte, a '
                      'confirmation written by the running firmware -- but expresses the flash '
                      "layout and the image format in Rust's type system so the parsing step "
                      'cannot run off the end of a buffer. There is no runtime interface: '
                      'everything is fixed at build time.',
        handoff='For bare-metal targets the handoff is the usual vector-table-and-branch. For '
                'Aarch64 Linux it loads the kernel and device tree and enters with the standard '
                'protocol, which is why it appears as a Type 3 bootloader spanning both roles '
                'on those boards.',
    ),
    'openblt': Bootloader(
        summary='Open-source bootloader for automotive and embedded MCUs.',
        boot_role='Provides firmware update over CAN, USB, UART or TCP/IP, then runs the '
                  'application.',
        type_rationale='Type 3: reset to application with an update path.',
        target='Application',
        stages=(
            Stage('reset into bootloader',
                  'OpenBLT occupies the first part of flash and runs at every reset.',
                  'reset handler entered'),
            Stage('backdoor window',
                  'For a short, configurable period it listens on the enabled transports -- '
                  'RS232, CAN, USB, TCP/IP, Modbus RTU -- for a host tool requesting an update.',
                  'no host session (or update done)'),
            Stage('firmware update',
                  'If a session is opened, XCP commands from MicroBoot or BootCommander erase '
                  'and program the application area; an SD card update path does the same from '
                  'a file.',
                  'new image written to flash'),
            Stage('checksum check',
                  "The application's signature/checksum word is verified.",
                  'checksum word valid'),
            Stage('application start',
                  'Vector table and stack pointer are set from the application and control '
                  'jumps to it.',
                  'vector table set, branch'),
        ),
        communication='The protocol between host and target is XCP over whichever transport is '
                      'configured, so the same PC tooling works across every supported MCU '
                      'family. On the target side the state is small and explicit: a checksum '
                      'word the bootloader writes and verifies, and a shared RAM location the '
                      'application can set before resetting to request that the backdoor stay '
                      'open -- the standard way an application triggers its own update.',
        handoff='Nothing is passed to the application beyond the hardware state; the bootloader '
                'remaps the vector table and branches. Because the backdoor window runs before '
                'verification and listens on external interfaces, it is the part of the design '
                'most relevant to the external-hardware and remote-access attack surfaces.',
    ),
    'redboot': Bootloader(
        summary='RedBoot, the eCos-based ROM monitor.',
        boot_role='Provides a debug monitor, flash management and network download, then boots '
                  'an image.',
        type_rationale='Type 3: it owns the board from reset.',
        target='Loaded image<br/>(Linux kernel or raw)',
        stages=(
            Stage('eCos start-up',
                  'RedBoot is an eCos application, so the eCos HAL runs first: exception '
                  'vectors, memory and cache setup.',
                  'eCos HAL, vectors, caches'),
            Stage('board init',
                  'Platform initialisation, then flash and network drivers are brought up.',
                  'flash + network drivers'),
            Stage('configuration load',
                  'Persistent configuration is read from the fconfig block in flash -- boot '
                  'script, IP settings, console baud rate.',
                  'fconfig: boot script, IP, baud'),
            Stage('boot script or prompt',
                  'A stored script runs after a timeout, or an interactive prompt is offered on '
                  'the console or over telnet.',
                  'chosen command'),
            Stage('image load and go',
                  'The image is loaded from flash, TFTP or serial, and `exec`/`go` transfers '
                  'control.',
                  'exec/go: cmdline + initrd, or bare address'),
        ),
        communication="RedBoot's interface is the command monitor: `fis` manages the flash "
                      'image system -- a simple table of named images in flash -- `fconfig` '
                      'edits persistent settings, and `load` fetches images over TFTP, HTTP or '
                      'X/Y-modem. It also implements the GDB remote protocol on the same '
                      'console, so a developer can debug the loaded program through the '
                      'bootloader. That combination of a network-reachable monitor and a debug '
                      'stub in the boot path is what makes it interesting as an attack surface.',
        handoff='`exec` starts a Linux kernel with a command line and optional initrd, `go` '
                'jumps to an arbitrary loaded address. Since it is built on eCos, it can also '
                'simply be linked with the application it boots.',
    ),
    'optiboot': Bootloader(
        summary='The small AVR bootloader shipped on most Arduino boards.',
        boot_role='Occupies the boot section, accepts an STK500 upload over serial, then jumps '
                  'to the sketch.',
        type_rationale='Type 3: reset to application on an 8-bit MCU.',
        target='Sketch<br/>(application)',
        stages=(
            Stage('reset into boot section',
                  'AVR fuses set the reset vector into the 512-byte boot section where Optiboot '
                  'lives.',
                  'boot section entered'),
            Stage('entry check',
                  'Decides whether to enter programming mode: a reset cause check, and a short '
                  'window waiting for STK500 activity on the UART.',
                  'no programmer present (or flash written)'),
            Stage('STK500v1 session',
                  'If a programmer is talking, receives pages over the serial line and writes '
                  'them to flash with SPM.',
                  'pages written via SPM'),
            Stage('application jump',
                  'Times out or finishes, then jumps to address 0 to start the sketch.',
                  'rjmp 0, MCUSR preserved in a register'),
        ),
        communication='Optiboot is 512 bytes, which dictates everything: the protocol is a '
                      'minimal subset of STK500v1 over the UART, there is no configuration '
                      'storage, and the only state passed to the application is the MCU status '
                      'register value, which Optiboot preserves in a register so the sketch can '
                      'tell a power-on reset from a watchdog reset. The `fastboot` behaviour -- '
                      'starting the application immediately unless a reset came from the right '
                      'source -- exists to avoid the delay a larger bootloader would impose.',
        handoff='The jump to the application is a bare `rjmp` to address 0. Nothing is '
                'verified: Optiboot has no signature checking, which is appropriate for its '
                'size and its role but makes physical access to the serial line equivalent to '
                'full control of the device.',
    ),
    'Adafruit_nRF52_Bootloader': Bootloader(
        summary='UF2 and DFU bootloader for nRF52 boards.',
        boot_role='Presents a USB mass-storage device for drag-and-drop firmware update, then '
                  'starts the application.',
        type_rationale='Type 3: reset to application.',
        target='Application',
        stages=(
            Stage('reset into bootloader',
                  'The nRF52 starts in the bootloader region; the MBR at the bottom of flash '
                  'handles vector forwarding.',
                  'MBR forwards to the bootloader'),
            Stage('DFU trigger check',
                  'Enters update mode on a double-tap reset, a GPIO condition, or a request '
                  'left by the application in a retained register.',
                  'GPREGRET / double-tap flag'),
            Stage('interface presentation',
                  'Presents itself as a USB mass-storage device for UF2 drag-and-drop, a CDC '
                  'serial port for nrfutil DFU, or over BLE.',
                  'UF2 mass storage, CDC or BLE'),
            Stage('image write',
                  'Writes the received image into the application region, checking the '
                  "package's CRC and, for nrfutil packages, its signature.",
                  'image in the application region'),
            Stage('application start',
                  'Sets the vector table through the MBR and starts the application.',
                  'MBR sets the vector table, branch'),
        ),
        communication="The channel between application and bootloader is the nRF52's retained "
                      'GPREGRET register plus a double-tap flag in RAM, which survive a soft '
                      'reset -- that is how an application asks to be re-entered into DFU '
                      'without a physical button. UF2 itself is a deliberately simple '
                      'container: 512-byte blocks each carrying their own target address and '
                      'block count, so a file copy onto a mass-storage device is a valid '
                      'flashing protocol even though the OS believes it is writing to FAT.',
        handoff='Control passes to the application through the Nordic MBR, which owns the real '
                'vector table and forwards interrupts to whichever image is running. Nothing '
                'else is passed. The UF2 path performs no signature check, which is the trade '
                'made for making firmware updates a drag-and-drop operation.',
    ),
    'katapult': Bootloader(
        summary='CAN, USB and UART bootloader for MCUs, common on 3D printer boards.',
        boot_role='Accepts firmware over its supported transports, then runs the application.',
        type_rationale='Type 3: reset to application.',
        target='Application<br/>(Klipper firmware)',
        stages=(
            Stage('reset into bootloader',
                  'Katapult occupies the start of flash and runs first on every reset.',
                  'reset handler entered'),
            Stage('entry decision',
                  'Stays in the bootloader if a request flag was left in a known RAM location, '
                  'a button is held, or no valid application is present.',
                  'RAM magic value or button state'),
            Stage('interface bring-up',
                  "Brings up CAN, USB or UART using Klipper's hardware abstraction layer, "
                  'stripped down.',
                  'CAN/USB/UART up, node addressable'),
            Stage('flashing session',
                  'Receives the application image in blocks and writes it to the application '
                  'region.',
                  'image in the application region'),
            Stage('application jump',
                  'Verifies the image checksum, then jumps to the application.',
                  'vector table set, branch'),
        ),
        communication="Katapult shares Klipper's HAL, so the bootloader and the application it "
                      'loads are built from the same driver code -- unusual, and the reason its '
                      'footprint is small. On CAN it uses the same node-identification scheme '
                      'as Klipper, so a toolhead board can be addressed by UUID on a shared '
                      'bus. The request to stay in the bootloader is passed from the '
                      'application through a magic value in RAM that survives a soft reset.',
        handoff='The jump is the standard Cortex-M vector-table relocation and branch, with '
                'nothing passed. Because flashing happens over a shared CAN bus, the relevant '
                'exposure is that any node able to speak on that bus can address the '
                'bootloader.',
    ),
    'tock-bootloader': Bootloader(
        summary='Bootloader for the Tock embedded OS.',
        boot_role='Flashes and verifies Tock applications over serial before starting the '
                  'kernel.',
        type_rationale='Type 3: reset to application.',
        target='Tock kernel',
        stages=(
            Stage('board start',
                  'The bootloader is itself a Tock kernel image: the board file initialises '
                  'chips, peripherals and the kernel.',
                  'chips and peripherals up'),
            Stage('entry check',
                  'Checks the bootloader entry condition -- typically a GPIO held at reset -- '
                  'to decide whether to run or pass through.',
                  'GPIO entry condition'),
            Stage('protocol service',
                  'Serves the Tock bootloader protocol over UART or USB CDC: read, write, '
                  'erase, get attributes.',
                  'flash written, attributes exposed'),
            Stage('application start',
                  'Jumps to the main Tock kernel image.',
                  'vector table set, branch'),
        ),
        communication="Because it is built on Tock itself, the bootloader reuses the kernel's "
                      'driver and capsule infrastructure rather than reimplementing it. Its '
                      'protocol is a simple framed command set that `tockloader` speaks, with '
                      'an attribute table stored in flash holding board name, architecture and '
                      'application addresses -- so the host tool discovers the flash layout '
                      'from the device instead of being configured for it.',
        handoff='Control passes to the real kernel image by the usual vector-table-and-branch. '
                'The design point of interest is that the bootloader is a full kernel: the '
                'isolation properties Tock provides for applications are available to the '
                'update path as well.',
    ),
    'STM32duino-bootloader': Bootloader(
        summary='USB DFU bootloader for STM32F1 boards.',
        boot_role='Enumerates as a DFU device for upload, then jumps to the sketch.',
        type_rationale='Type 3: reset to application.',
        target='Sketch<br/>(application)',
        stages=(
            Stage('reset into bootloader',
                  'Occupies the first 8 or 16 KB of STM32F1 flash.',
                  'flash base entered'),
            Stage('button/flag check',
                  'Checks the BOOT jumper, a button, or a magic value left in a backup register '
                  'by the application.',
                  'BOOT jumper or backup-register magic'),
            Stage('USB DFU enumeration',
                  'Enumerates as a USB DFU device using the bundled ST USB library.',
                  'DFU endpoint enumerated'),
            Stage('download',
                  'Receives the application image over DFU and writes it to the application '
                  'offset.',
                  'image at the agreed offset'),
            Stage('application jump',
                  'Relocates the vector table to the application offset and jumps.',
                  'VTOR relocated, branch'),
        ),
        communication='The bootloader and the Arduino core agree on a flash offset (0x8002000 '
                      'or 0x8005000) and on the backup-register magic value that means "reset '
                      'into DFU" -- that pair is the entire interface. Because the vector table '
                      'has to be moved, the application must set VTOR to the same offset, which '
                      'is why an image built for the wrong offset simply hangs.',
        handoff='Nothing is passed to the application. There is no verification of what was '
                'downloaded; the USB DFU path is open whenever the device is in bootloader '
                'mode, which is the characteristic exposure of this class of hobbyist '
                'bootloader.',
    ),
    'mbed-bootloader': Bootloader(
        summary='Mbed OS bootloader with firmware update support.',
        boot_role='Verifies and applies an update image, then boots the Mbed application.',
        type_rationale='Type 3: reset to application.',
        target='Application',
        stages=(
            Stage('reset into bootloader',
                  'Runs first from the start of flash.',
                  'reset handler entered'),
            Stage('update candidate check',
                  'Looks for a firmware candidate in internal or external storage, placed there '
                  'by Pelion Device Management Client.',
                  'candidate image + metadata header'),
            Stage('verification',
                  "Checks the candidate's hash and signature against the manifest the update "
                  'client validated.',
                  'hash and signature verified'),
            Stage('copy',
                  'Copies the candidate into the active application region, tracking progress '
                  'so an interrupted copy resumes.',
                  'candidate copied into the active slot'),
            Stage('application start',
                  'Jumps to the active application.',
                  'branch to the active application'),
        ),
        communication='The bootloader and the update client communicate through a firmware '
                      'metadata header written alongside each image -- version, size, hash and '
                      'signature -- kept in a known location so the bootloader can make its '
                      'decision without the client running. The active and candidate headers '
                      'are duplicated so a power loss during the header write cannot leave an '
                      'ambiguous state.',
        handoff='The jump to the application passes nothing. Its role in the corpus is as the '
                'device-side half of a managed OTA pipeline: the interesting security '
                'properties are in the manifest format and the key provisioning, not in the '
                'boot flow itself.',
    ),
    'IMBootloader': Bootloader(
        summary='IMProject bootloader for STM32.',
        boot_role='CRC-checked firmware update over UART or USB, then application start.',
        type_rationale='Type 3: reset to application.',
        target='Application',
        stages=(
            Stage('startup',
                  'Vendor startup code and the linker script place the bootloader at the base '
                  'of flash.',
                  'vector table from the linker script'),
            Stage('entry check',
                  'Decides whether to enter update mode based on a flag or host activity.',
                  'update flag or host activity'),
            Stage('host session',
                  'Talks to the IMFlasher host tool over USB or UART.',
                  'image received over USB/UART'),
            Stage('verification',
                  'Checks the image signature using Monocypher before accepting it.',
                  'Monocypher signature verified'),
            Stage('application jump',
                  'Writes the image to the application region and jumps to it.',
                  'image written, branch'),
        ),
        communication='The design goal is that one bootloader plus one host tool serve every '
                      'supported MCU, so the board differences are pushed into the Drivers and '
                      'Linker directories and the protocol above them stays fixed. Monocypher '
                      'provides the signature check in a small enough footprint to fit '
                      'alongside the rest. Update metadata travels in the protocol rather than '
                      'in a flash header.',
        handoff='Nothing is passed to the application beyond the vector table relocation. Its '
                'interest in the corpus is as a small, current example of a signed-update '
                'bootloader that is explicitly designed to be reused across MCU families.',
    ),
    'stm32-mw-openbl': Bootloader(
        summary='STMicroelectronics OpenBootLoader middleware.',
        boot_role='Reimplements the STM32 system bootloader protocol in open source.',
        type_rationale='Type 3: the in-ROM-equivalent stage that owns the MCU from reset.',
        target='Address chosen by the host',
        stages=(
            Stage('reset or jump into Open Bootloader',
                  'Runs from wherever it was linked in user flash, having been started at reset '
                  'or jumped to by the application.',
                  'linked address entered'),
            Stage('HAL initialisation',
                  'Brings up clocks, power and the configured interfaces through STM32Cube '
                  'HAL/LL drivers.',
                  'clocks, power, interfaces up'),
            Stage('interface detection',
                  'Waits for a host on USART, I2C, SPI, USB-DFU or FDCAN and locks onto the '
                  'first that speaks.',
                  'host locked onto one interface'),
            Stage('command service',
                  'Serves the ST system bootloader command set -- Get, Read Memory, Write '
                  'Memory, Erase, Go, and the protection commands.',
                  'Get/Read/Write/Erase served'),
            Stage('Go',
                  'The Go command transfers control to an address the host specifies.',
                  'Go: SP and PC set from the host'),
        ),
        communication='Open Bootloader is deliberately protocol-compatible with the system '
                      'bootloader in STM32 ROM, so STM32CubeProgrammer and any tool written '
                      "against AN3155 work unchanged -- the communication contract is ST's "
                      'published command set rather than anything new. It runs in the non- '
                      'secure domain and relies on flash write protection to keep itself from '
                      'being overwritten by its own commands.',
        handoff='The `Go` command sets the stack pointer and program counter from the address '
                'given and branches, so what the application receives is whatever the host '
                'chose. That is the intended flexibility and also the reason it belongs behind '
                'readout and write protection: a reachable Open Bootloader is an arbitrary '
                'read/write/execute interface to the device.',
    ),
    'harmony': Bootloader(
        summary='Microchip Harmony bootloader framework.',
        boot_role='Configurable bootloader for PIC and SAM devices with several update '
                  'transports.',
        type_rationale='Type 3: reset to application.',
        target='Application',
        stages=(
            Stage('reset into bootloader',
                  'The Harmony bootloader occupies the reset region of the PIC32 or SAM device.',
                  'reset region entered'),
            Stage('trigger evaluation',
                  'A configurable trigger -- GPIO, a RAM pattern written by the application, or '
                  'a missing valid application -- decides whether to enter update mode.',
                  'GPIO, RAM pattern or missing image'),
            Stage('transport service',
                  'Serves the selected transport: UART, USB (device or host), CAN, Ethernet/UDP '
                  'or SD card.',
                  'transport session open'),
            Stage('programming',
                  'Receives the image, optionally verifies a CRC or signature, and writes it to '
                  'the application region -- with a dual-bank variant that programs the '
                  'inactive bank.',
                  'image written (or inactive bank programmed)'),
            Stage('application jump',
                  "Transfers control to the application's reset address.",
                  'branch to the reset vector, or bank swap'),
        ),
        communication="Harmony's bootloader is generated rather than hand-written: MPLAB "
                      'Harmony Configurator emits the bootloader for the chosen device and '
                      'transports, so the stage structure is fixed and the variation is in '
                      'configuration. The application signals a wish to re-enter the bootloader '
                      'through a trigger pattern in a RAM region both sides agree on, checked '
                      'before RAM is initialised.',
        handoff="The jump is a branch to the application's reset vector with nothing passed. In "
                'the dual-bank configuration the handoff is instead a bank swap at reset, which '
                'makes the update atomic and the fallback automatic.',
    ),
    'arduino-variometer': Bootloader(
        summary='Arduino variometer project including its bootloader.',
        boot_role='Application firmware with a small bootloader for a flight instrument.',
        type_rationale='Type 3: reset to application on AVR.',
        target='Flight instrument<br/>(running)',
        stages=(
            Stage('bootloader',
                  'A stock AVR bootloader (Optiboot or similar) occupies the boot section and '
                  'provides serial programming.',
                  'rjmp 0 to the sketch'),
            Stage('application start',
                  'The variometer firmware starts and initialises its sensors -- barometer, '
                  'accelerometer, magnetometer, GPS.',
                  'sensors initialised'),
            Stage('calibration data load',
                  'Calibration values are read from EEPROM, where the separate calibration '
                  'sketches in this repository wrote them.',
                  'calibration values from EEPROM'),
            Stage('main loop',
                  'Runs the flight instrument: sensor fusion, display and audio output, '
                  'logging.',
                  'sensor fusion, display and audio'),
        ),
        communication='This project is application firmware with a conventional AVR bootloader '
                      'beneath it, and the only state crossing that boundary is EEPROM: '
                      'calibration written by one sketch is read by another. It is included in '
                      'the corpus as a worked example of the Type 3 pattern at its simplest -- '
                      'reset goes to a small serial-programmable loader, which goes to an '
                      'application that owns the device -- rather than for the bootloader being '
                      'novel.',
        handoff="The jump to the application is the AVR bootloader's `rjmp` to address 0, with "
                'nothing passed. There is no verification anywhere in the path.',
    ),
    'firmware': Bootloader(
        summary='Meshtastic device firmware.',
        boot_role='ESP32 and nRF52 firmware for LoRa mesh radios, including its update path.',
        type_rationale='Type 3: device firmware that owns the MCU from reset.',
        target='Meshtastic application',
        stages=(
            Stage('SoC ROM / second-stage loader',
                  'On ESP32 the mask ROM loads the second-stage bootloader from flash; on nRF52 '
                  "an existing bootloader (Adafruit's or Nordic's) occupies that role.",
                  'second-stage bootloader from flash'),
            Stage('partition selection',
                  'The bootloader reads the partition table and the OTA data partition to '
                  'decide which application slot to run.',
                  'partition table + otadata slot pointer'),
            Stage('verification',
                  "Where secure boot and flash encryption are enabled, the application image's "
                  'signature is checked and its flash is decrypted.',
                  'signature checked, flash decrypted'),
            Stage('application start',
                  'The Meshtastic firmware starts: radio, display, GPS, and the mesh stack.',
                  'radio, display and mesh stack up'),
            Stage('OTA update',
                  'New images are received over the network or USB, written to the inactive '
                  'slot, and marked for the next boot.',
                  'new image staged in the inactive slot'),
        ),
        communication='The boot-time interface is the ESP-IDF one: a partition table in flash, '
                      'an `otadata` partition holding the active-slot pointer and rollback '
                      'state, and NVS for configuration the application persists. The '
                      'application marks a new image valid after it has run successfully, and '
                      'the bootloader reverts to the previous slot if that never happens -- the '
                      "same confirm-or-rollback contract MCUboot uses, expressed in Espressif's "
                      'format.',
        handoff='The bootloader jumps to the selected application image with nothing passed '
                'beyond what the partition table and otadata already determined. This entry is '
                'device firmware rather than a general bootloader, and it is in the corpus '
                'because its A/B update path and its network-facing update surface are the '
                'parts that matter for bootloader security.',
    ),
}
