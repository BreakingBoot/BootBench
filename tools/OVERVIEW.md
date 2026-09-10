# Bootloader analysis tools: what works, and on what

Which of the 24 tools in [`../analysis-tools/`](../analysis-tools/) run, which
bootloaders each one applies to, and what the rest need.

Run any of them with:

```bash
./scripts/analysis/run-tool.sh <tool> <target>
./scripts/analysis/run-tool.sh --list
```

Everything works through docker, so the host needs no toolchain. Results land
in `analysis-results/<tool>/<target>/`.

Generated from [`analysis_runners.json`](analysis_runners.json) by
`generate_overview.py` — edit the manifest, not this file.


## Working — 18 of 24

| Tool | Applies to | Verified on |
|------|-----------|-------------|
| [`angr`](../analysis-tools) | Any compiled bootloader: ELF (U-Boot sandbox, kexec) or PE (shim, GRUB, any DXE module). Raw blobs need --base and --arch. | **shimx64.efi** — 3,017 functions; OVMF MnpDxe -> CFG recovered |
| [`arbiter`](../analysis-tools) | Compiled bootloader binaries, x86/x86-64. Needs a template naming the sinks. | **kexec** — 10 integer-overflow findings with taint histories |
| [`binwalk`](../analysis-tools) | Any firmware image or flash dump, UEFI or embedded. | **OVMF.fd** — LZMA DXE volume + SecMain PE located |
| [`BootStomp`](../analysis-tools) | Android bootloaders only: Qualcomm LK (type2/lk), Huawei fastboot, Nexus hboot, Xperia LK. Needs a per-image config. | **Qualcomm LK (unpatched, bundled)** — 2 sink alerts, 2 loop alerts, 1 dereference alert |
| [`chipsec`](../analysis-tools) | UEFI firmware images offline. On-target platform checks need the live machine. | **OVMF.fd** — EFI volumes parsed offline (chipsec_util -n uefi decode) |
| [`codeql`](../analysis-tools) | Any bootloader that builds. Recipes for 15 in build_commands.json; U-Boot and barebox use sandbox targets, coreboot builds its own toolchain. | **kexec-tools (source)** — 78 results, 7 cpp/unbounded-write, 3 cpp/path-injection |
| [`efi_fuzz`](../analysis-tools) | UEFI DXE and SMM drivers from EDK-II or an OEM image. Ships three worked examples. | **smram_arbitrary_write example** — DXE driver emulated, SMM protocols initialised |
| [`emba`](../analysis-tools) | Whole firmware images, UEFI or Linux-based embedded. Broad rather than bootloader-specific. | **OVMF.fd** — full scan, HTML report generated |
| [`fiano`](../analysis-tools) | UEFI firmware images, same as UEFITool. Go-based, good for scripting. | **OVMF.fd** — full FV/file/section tree |
| [`fwhunt-scan`](../analysis-tools) | Individual UEFI modules (PE32+) from EDK-II, Project Mu or an OEM image. | **OVMF MnpDxe** — 94 boot services, 32 protocols, 11 GUIDs |
| [`fwupd`](../analysis-tools) | Any firmware blob, offline. Identifies the container format and hashes it as Secure Boot would. | **shimx64.efi** — Authenticode hash and PE section layout |
| [`karonte`](../analysis-tools) | Firmware binaries with multiple communicating components. Ships configs for Qualcomm LK (type2/lk). | **Qualcomm LK (unpatched, staged from BootStomp)** — completed, tainted-path report written |
| [`MEAnalyzer`](../analysis-tools) | Intel ME/CSME/TXE regions, which sit beside the bootloader in the same flash part. Not present in OVMF. | **OVMF.fd** — correctly reports no Intel ME region present |
| [`pesign`](../analysis-tools) | Signed PE bootloaders: shim, GRUB's EFI build, systemd-boot, any signed DXE module. | **shimx64.efi** — signed by Microsoft Corporation UEFI CA 2011 |
| [`top4grep`](../analysis-tools) | Not a bootloader tool: searches conference proceedings. | **keyword 'bootloader'** — 4 papers across the top-4 venues |
| [`uefi-firmware-parser`](../analysis-tools) | UEFI firmware images plus Intel flash descriptors. | **OVMF.fd** — firmware volumes, SecMain, PE32 sections |
| [`uefi_retool`](../analysis-tools) | UEFI firmware images, for module extraction only. Protocol recovery needs IDA Pro. | **OVMF.fd** — 113 named UEFI modules extracted |
| [`UEFITool`](../analysis-tools) | UEFI firmware images: OVMF from edk2, Project Mu builds, OEM flash dumps. | **OVMF.fd** — 578 entries; --extract yielded 1,471 files |

## Blocked — 6

| Tool | Applies to | What it needs |
|------|-----------|---------------|
| `ASPFuzz` | The AMD Secure Processor on-chip bootloader only. | Targets the AMD Secure Processor ROM on specific silicon. |
| `emmutaler` | Apple iBoot only. | Needs decrypted Apple iBoot images, which are not distributable. |
| `FACT_core` | Whole firmware images of any kind. | Multi-container deployment with its own database, worker pool and web UI, installed by its own scripts against the host. Analyses whole firmware images rather than bootloaders specifically. |
| `firmadyne` | Linux-based router and IoT firmware images. Not bootloaders. | Same architecture as FirmAE and superseded by it: needs a host PostgreSQL database plus prebuilt QEMU kernels. Emulates Linux router firmware, not bootloaders. |
| `FirmAE` | Linux-based router and IoT firmware images. Not bootloaders. | Its download.sh and docker-init.sh do run unattended (the fcore image builds), but init.sh then does `sudo service postgresql restart` against a PostgreSQL instance on the host, which the fcore image does not contain. It also emulates Linux router firmware, so BootBench holds no target for it. |
| `tsffs` | Anything Simics can simulate, including UEFI and embedded bootloaders. | Requires Intel Simics, which is not freely redistributable. |

## Which tool for which bootloader

The corpus is source, so most tools need something built first.

| You have | Use |
|----------|-----|
| Bootloader **source** that compiles | `codeql` |
| A compiled **ELF or PE** bootloader | `angr`, `arbiter` |
| A signed **.efi** (shim, GRUB, systemd-boot) | `pesign`, `fwupd`, `angr` |
| A **UEFI firmware image** (OVMF, OEM dump) | `UEFITool`, `fiano`, `uefi-firmware-parser`, `uefi_retool`, `binwalk`, `chipsec`, `emba` |
| A single **UEFI module** pulled from one | `fwhunt-scan`, `angr`, `efi_fuzz` |
| An **Android bootloader** (LK, hboot) | `BootStomp`, `karonte` |
| An **Intel ME region** | `MEAnalyzer` |

To get a UEFI image out of the corpus, build OVMF from `type1/edk2` and
extract its modules with `UEFITool --extract`; both are described in
[`../scripts/analysis/README.md`](../scripts/analysis/README.md).

## Patches

Five tools needed code changes or a specific environment to run at all.
[`../scripts/analysis/PATCHES.md`](../scripts/analysis/PATCHES.md) documents
each, and the runners apply the patches automatically — the submodules are
left untouched.
