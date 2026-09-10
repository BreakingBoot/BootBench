# fiano

*Go tooling to read, modify and rebuild UEFI images.*

| | |
|---|---|
| Category | Image inspection and reverse engineering |
| Consumes | firmware-image |
| Status | `runnable` |
| Upstream | https://github.com/linuxboot/fiano |
| Language | Go |

## What it does

Walk and rebuild UEFI images (utk).

## What it applies to

UEFI firmware images, same as UEFITool. Go-based, good for scripting.

## Verified run

Run against **OVMF.fd**: full FV/file/section tree

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh fiano <target>

# results
ls analysis-results/fiano/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

You supply the image.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
