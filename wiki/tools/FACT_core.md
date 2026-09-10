# FACT_core

*Firmware analysis and comparison framework.*

| | |
|---|---|
| Category | Image inspection and reverse engineering |
| Consumes | firmware-image |
| Status | `manual` |
| Upstream | https://github.com/fkie-cad/FACT_core |
| Language | Python |

## What it does

Firmware analysis and comparison framework with a web UI.

## What it applies to

Whole firmware images of any kind.

## Running it

No runner is provided. Multi-container deployment with its own database, worker pool and web UI, installed by its own scripts against the host. Analyses whole firmware images rather than bootloaders specifically.

## Notes

Multi-container deployment; follow the project's docker-compose setup.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
