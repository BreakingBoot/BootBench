# UEFITool

*Parse, browse and modify UEFI firmware images.*

| | |
|---|---|
| Category | Image inspection and reverse engineering |
| Consumes | firmware-image |
| Status | `runnable` |
| Upstream | https://github.com/LongSoft/UEFITool |
| Language | C |

## What it does

Browse and edit UEFI images; UEFIExtract is the CLI.

## What it applies to

UEFI firmware images: OVMF from edk2, Project Mu builds, OEM flash dumps.

## Verified run

Run against **OVMF.fd**: 578 entries; --extract yielded 1,471 files

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh UEFITool <target>

# results
ls analysis-results/UEFITool/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

UEFIExtract report/unpack; --extract yields the individual DXE modules.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
