# top4grep

*Grep the top four security conferences; the SoK's literature search tool.*

| | |
|---|---|
| Category | Literature search |
| Consumes | corpus |
| Status | `runnable` |
| Upstream | https://github.com/Kyle-Kyle/top4grep |
| Language | Python |

## What it does

Grep the top four security conferences.

## What it applies to

Not a bootloader tool: searches conference proceedings.

## Verified run

Run against **keyword 'bootloader'**: 4 papers across the top-4 venues

## Walkthrough

```bash
# what this tool can be pointed at
./scripts/analysis/run-tool.sh --list

# run it
./scripts/analysis/run-tool.sh top4grep <target>

# results
ls analysis-results/top4grep/
```

The first run builds a container image, which can take a while. Everything afterwards reuses it. Output ownership is handed back to you on exit, including when a run fails.

## Notes

Needs nltk corpora in the image. tools/collect_papers.py covers eight venues instead of four.

---

[Home](Home) · [Tools](Tools) · [Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)
