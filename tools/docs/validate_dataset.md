# `validate_dataset.py`

Consistency checks across all three data submodules. Exits non-zero on failure,
so it works as a CI gate.

## Run it

```bash
python3 validate_dataset.py --root ..
python3 validate_dataset.py --root .. --check classification --check coverage
```

| Flag | Purpose |
|---|---|
| `--root DIR` | BootBench checkout root. Default `..`. |
| `--check NAME` | Run one check. Repeatable, default all six. |

## The checks

| Check | What it asserts |
|---|---|
| `classification` | Replaying the keyword rules over each published `results.json` reproduces the committed keyword breakdown, and no type's exclude list rejects its own CVEs. |
| `cves` | Each `cves/` directory holds exactly one record per results entry. |
| `records` | No CVE is counted under two types; no CVE withdrawn upstream is still counted. |
| `stats` | The vulnerability-type rows in each `stats.md` sum to the total that file states. |
| `coverage` | `.gitmodules`, the directories on disk, and the mined output agree. |
| `commits` | The summary covers every mined repository, and parent links point backwards in time. |

## Current findings

On the dataset as published, `classification` and `cves` pass and the other four
report real data problems — 11 findings in total. These are *dataset* issues,
not tool failures; each is measured in [improvements.md](improvements.md). Fixing them means re-mining, which changes numbers the paper
cites; use [`refresh_dataset.py`](refresh_dataset.md) to stage and review that.
