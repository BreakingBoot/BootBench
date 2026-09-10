# uefi_retool

*IDA tooling for reverse engineering UEFI modules and protocols.*

| | |
|---|---|
| Category | Image inspection and reverse engineering |
| Consumes | binary |
| Status | `runnable` |
| Upstream | https://github.com/yeggor/uefi_retool |
| Language | Python |

## What it does

IDA tooling for UEFI protocol and module reverse engineering.

## What it applies to

UEFI firmware images, for module extraction only. Protocol recovery needs IDA Pro.

## Verified run

Run against **OVMF.fd**: 113 named UEFI modules extracted

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh uefi_retool <target>

# results
ls analysis-results/uefi_retool/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Only the IDA-free half. get-info and get-pp drive IDA Pro; get-images does not.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
