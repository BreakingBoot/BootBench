# Attack surfaces

The six surfaces the SoK defines, and how the dataset maps onto them. Every CVE and every mined commit carries an `attack_surfaces` field listing the surfaces its text touches, with the matched wording recorded so a classification can be checked.

| | Kind | Surface | Reached through |
|---|---|---|---|
| `SAS3` | software | Post-boot features | SMM, SMI handlers, UEFI Runtime Services — code still live after the OS starts |
| `SAS1` | software | Remote access | PXE, TFTP, DHCP, HTTP boot, iSCSI — anything the bootloader fetches over a network |
| `SAS4` | software | Boot-time features | Boot menus, GRUB and UEFI shells, recovery and download modes |
| `SAS2` | software | Persistent data source | Variables, configuration files, partition tables, filesystems, boot logos, ACPI tables |
| `HAS2` | hardware | External hardware | USB, DMA, PCIe, removable media — a device an attacker can attach |
| `HAS1` | hardware | Invasive hardware | SPI flash, JTAG, glitching — an attacker who opens the case |

## What the data shows

Primary surface per CVE, by bootloader type. The primary is the highest-precedence surface present, not a judgement about which mattered most.

| Type | `SAS3` | `SAS1` | `SAS4` | `SAS2` | `HAS2` | `HAS1` |
|---|---|---|---|---|---|---|
| Firmware bootloader | 253 | 19 | 9 | 58 | 7 | 2 |
| OS bootloader | 1 | 45 | 24 | 44 | 8 | 6 |
| Monolithic bootloader | 0 | 17 | 2 | 26 | 1 | 2 |

The shape matches the taxonomy. Type 1 is dominated by post-boot features — SMM and runtime services are what a firmware bootloader leaves running. Type 2 spreads across persistent data sources, remote access and boot-time features, which is what a configuration-driven, network-capable OS loader exposes. Type 3 concentrates in persistent data sources, because a monolithic bootloader's attack surface is mostly the images and data it parses.

## Limits

Mapping is done on the text of a CVE description or commit message, so it inherits their vagueness. Around a third of CVEs and a sixth of commits map to any surface at all; the rest simply do not say enough. A description that mentions PXE in passing will be counted as remote access even if the flaw is in configuration parsing — BootHole is exactly that case.
