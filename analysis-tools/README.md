# Bootloader analysis tools

The tools BootBench exists to evaluate, collected as submodules so a given
version can be pinned alongside the dataset. Pointers only — no vendored code.

The SoK found that most bootloader analysis tools are tied to one
implementation and cover one attack surface: of the 25 techniques it surveyed,
only 3 covered more than one. This directory is the practical side of that
finding — what is actually available to run.

See [`tools/OVERVIEW.md`](../tools/OVERVIEW.md) for which of these run, and
what each one applies to.

```bash
git submodule update --init --recursive analysis-tools     # all of them
git submodule update --init analysis-tools/dynamic/tsffs   # or just one
```

Regenerate this file with:

```bash
python3 tools/generate_tools_table.py --output analysis-tools/README.md
```


## Contents

- [Static analysis](#static-analysis) — 6
- [Dynamic analysis, fuzzing and rehosting](#dynamic-analysis-fuzzing-and-rehosting) — 7
- [Image inspection and reverse engineering](#image-inspection-and-reverse-engineering) — 7
- [Platform assessment and signing](#platform-assessment-and-signing) — 3
- [Literature search](#literature-search) — 1

## Static analysis

| Tool | What it does | Language | Stars | Last push |
|------|--------------|----------|------:|-----------|
| [codeql](https://github.com/github/codeql) | Query engine behind the SoK's static evaluation; CodeQL databases over bootloader source. | CodeQL | 10,063 | 2026-09-08 |
| [angr](https://github.com/angr/angr) | Binary analysis platform: symbolic execution and static analysis over stripped firmware. | Python | 9,073 | 2026-09-09 |
| [karonte](https://github.com/ucsb-seclab/karonte) | Static taint tracking across firmware binaries and their IPC boundaries. | Python | 430 | 2021-09-18 |
| [BootStomp](https://github.com/ucsb-seclab/BootStomp) | Taint analysis for Android bootloaders; the first bootloader-specific detector. | Python | 417 | 2022-01-10 |
| [fwhunt-scan](https://github.com/binarly-io/fwhunt-scan) | Rule-based scanner for known UEFI threats and vulnerable modules. | Python | 244 | 2025-05-02 |
| [arbiter](https://github.com/jkrshnmenon/arbiter) | Static and symbolic detection of the bug classes the SoK evaluates. | Python | 239 | 2024-01-14 |

## Dynamic analysis, fuzzing and rehosting

| Tool | What it does | Language | Stars | Last push |
|------|--------------|----------|------:|-----------|
| [emba](https://github.com/e-m-b-a/emba) | Firmware analysis orchestrator; runs extraction and many checks in one pass. | Shell | 3,653 | 2026-09-07 |
| [firmadyne](https://github.com/firmadyne/firmadyne) | Emulation-based dynamic analysis of Linux firmware images. | Shell | 2,105 | 2024-07-21 |
| [FirmAE](https://github.com/pr0v3rbs/FirmAE) | Arbitrated emulation; raises firmware rehosting success rates over firmadyne. | Python | 923 | 2026-06-24 |
| [tsffs](https://github.com/intel/tsffs) | Simics-based fuzzer targeting firmware and UEFI boot paths. | Rust | 331 | 2026-09-03 |
| [emmutaler](https://github.com/galli-leo/emmutaler) | Fuzzer for Apple's iBoot second-stage bootloader. | Go | 168 | 2021-09-18 |
| [efi_fuzz](https://github.com/Sentinel-One/efi_fuzz) *(archived)* | Fuzzer for UEFI DXE drivers, built on a DXE emulator. | Python | 154 | 2025-05-02 |
| [ASPFuzz](https://github.com/TeumessianFox/ASPFuzz) | Fuzzer for the AMD Secure Processor on-chip bootloader. | Rust | 31 | 2023-04-12 |

## Image inspection and reverse engineering

| Tool | What it does | Language | Stars | Last push |
|------|--------------|----------|------:|-----------|
| [binwalk](https://github.com/ReFirmLabs/binwalk) | Firmware extraction and filesystem carving. | Rust | 14,322 | 2026-08-11 |
| [UEFITool](https://github.com/LongSoft/UEFITool) | Parse, browse and modify UEFI firmware images. | C | 5,662 | 2026-07-29 |
| [FACT_core](https://github.com/fkie-cad/FACT_core) | Firmware analysis and comparison framework. | Python | 1,465 | 2026-09-08 |
| [MEAnalyzer](https://github.com/platomav/MEAnalyzer) | Analyse Intel ME/CSME/TXE firmware regions. | Python | 1,323 | 2026-09-06 |
| [uefi-firmware-parser](https://github.com/theopolis/uefi-firmware-parser) | Parse UEFI volumes and Intel flash descriptors from Python. | Python | 922 | 2026-06-04 |
| [fiano](https://github.com/linuxboot/fiano) | Go tooling to read, modify and rebuild UEFI images. | Go | 373 | 2026-05-14 |
| [uefi_retool](https://github.com/yeggor/uefi_retool) *(archived)* | IDA tooling for reverse engineering UEFI modules and protocols. | Python | 368 | 2024-12-28 |

## Platform assessment and signing

| Tool | What it does | Language | Stars | Last push |
|------|--------------|----------|------:|-----------|
| [fwupd](https://github.com/fwupd/fwupd) | Firmware update service; the delivery side of the boot chain. | C | 4,148 | 2026-09-08 |
| [chipsec](https://github.com/chipsec/chipsec) | Platform security assessment: SMM, SPI, Secure Boot and chipset configuration. | Python | 3,298 | 2026-09-02 |
| [pesign](https://github.com/rhboot/pesign) | Sign and inspect PE binaries for Secure Boot. | C | 126 | 2026-08-07 |

## Literature search

| Tool | What it does | Language | Stars | Last push |
|------|--------------|----------|------:|-----------|
| [top4grep](https://github.com/Kyle-Kyle/top4grep) | Grep the top four security conferences; the SoK's literature search tool. | Python | 202 | 2026-06-05 |

## Manifest

[`tools/analysis_tools.json`](../tools/analysis_tools.json) drives both this file and [`scripts/add-analysis-tools.sh`](../scripts/add-analysis-tools.sh). Add an entry there, run the script, and regenerate this README.
