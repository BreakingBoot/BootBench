# uefi-firmware-parser

*Parse UEFI volumes and Intel flash descriptors from Python.*

| | |
|---|---|
| Category | Image inspection and reverse engineering |
| Consumes | firmware-image |
| Status | `runnable` |
| Upstream | https://github.com/theopolis/uefi-firmware-parser |
| Language | Python |

## What it does

Parse UEFI volumes, files and the Intel flash descriptor.

## What it applies to

UEFI firmware images plus Intel flash descriptors.

## Verified run

Run against **OVMF.fd**: firmware volumes, SecMain, PE32 sections

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh uefi-firmware-parser <target>

# results
ls analysis-results/uefi-firmware-parser/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

You supply the image.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
