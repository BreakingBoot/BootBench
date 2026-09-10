# binwalk

*Firmware extraction and filesystem carving.*

| | |
|---|---|
| Category | Image inspection and reverse engineering |
| Consumes | firmware-image |
| Status | `runnable` |
| Upstream | https://github.com/ReFirmLabs/binwalk |
| Language | Rust |

## What it does

Identify and carve structures out of a flash dump.

## What it applies to

Any firmware image or flash dump, UEFI or embedded.

## Verified run

Run against **OVMF.fd**: LZMA DXE volume + SecMain PE located

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh binwalk <target>

# results
ls analysis-results/binwalk/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

You supply the image; the corpus holds source, not builds.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
