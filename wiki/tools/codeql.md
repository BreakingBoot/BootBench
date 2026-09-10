# codeql

*Query engine behind the SoK's static evaluation; CodeQL databases over bootloader source.*

| | |
|---|---|
| Category | Static analysis |
| Consumes | source |
| Status | `runnable` |
| Upstream | https://github.com/github/codeql |
| Language | CodeQL |

## What it does

Build a CodeQL database from a bootloader build, run a query suite.

## What it applies to

Any bootloader that builds. 7 of 16 recipes in build_commands.json are verified end to end -- edk2, grub, kexec-tools, petitboot, seabios, shim, u-boot -- covering all three types. The rest are untested, and some need cross toolchains the image does not carry.

## Verified run

Run against **kexec-tools, seabios, petitboot**: 78 / 417 / 59 results including unbounded writes and uncontrolled path expressions; u-boot database builds, its query run is long

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh codeql <target>

# results
ls analysis-results/codeql/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Needs a working build; recipes in tools/build_commands.json.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
