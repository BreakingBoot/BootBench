# BootBench tools

The programs that build BootBench: collect the bootloader corpus, mine CVEs and
vulnerability-fixing commits, search the literature, and check that the result
is internally consistent.

Python 3.10+, standard library only, plus `git` on `PATH`. Nothing to install.

```bash
python3 test_tools.py            # 47 tests, no network needed
python3 validate_dataset.py --root ..
```

**[`OVERVIEW.md`](OVERVIEW.md)** answers the question people actually arrive
with: which analysis tools work, and which bootloaders each one applies to.

## The tools

| Tool | Does | Docs |
|---|---|---|
| [`classify_cves.py`](classify_cves.py) | Mine cvelistV5 for bootloader CVEs, assign each a type | [docs](docs/classify_cves.md) |
| [`cve_stats.py`](cve_stats.py) | Split results into per-CVE records, render `stats.md` | [docs](docs/cve_stats.md) |
| [`extract_vuln_commits.py`](extract_vuln_commits.py) | Mine bootloader git histories for vulnerability fixes | [docs](docs/extract_vuln_commits.md) |
| [`collect_papers.py`](collect_papers.py) | Find bootloader papers across the eight surveyed venues | [docs](docs/collect_papers.md) |
| [`generate_table.py`](generate_table.py) | Render the bootloader inventory table | [docs](docs/generate_table.md) |
| [`link_cves_to_commits.py`](link_cves_to_commits.py) | Join CVEs to their fixing commits and vulnerable parents | [docs](docs/link_cves_to_commits.md) |
| [`validate_dataset.py`](validate_dataset.py) | Consistency checks across all three submodules | [docs](docs/validate_dataset.md) |
| [`refresh_dataset.py`](refresh_dataset.py) | Stage a refresh, diff it, apply only on request | [docs](docs/refresh_dataset.md) |
| [`generate_tools_table.py`](generate_tools_table.py) | Render `analysis-tools/README.md` from the tool manifest | [docs](docs/generate_tools_table.md) |
| [`generate_overview.py`](generate_overview.py) | Render [`OVERVIEW.md`](OVERVIEW.md) from the runner manifest | — |
| [`test_tools.py`](test_tools.py) | Test suite for all of the above | [docs](docs/test_tools.md) |

[`dropped_security_commits.json`](dropped_security_commits.json) holds 28
commits the old substring matcher caught by accident that are genuinely
security-relevant but that the current word-bounded rules miss. Keeping them
recorded is deliberate: widening the keywords to catch them costs about 100
extra records each.

Two JSON manifests sit alongside them:
[`analysis_tools.json`](analysis_tools.json) (24 bootloader analysis tools) and
[`new_bootloaders.json`](new_bootloaders.json) (bootloaders queued for the
corpus). Both drive a script in [`../scripts/`](../scripts/), and the first also
renders `analysis-tools/README.md`.

[`bootbench_keywords.py`](bootbench_keywords.py) is not a tool. It holds the
classification rules — bootloader-type keywords, vulnerability keywords, CWE
aliases, paper search terms and contribution categories — as reviewable data.
Those rules previously existed only as inline shell arguments inside a GitHub
Actions workflow.

## Pipeline

```
                       ┌─ classify_cves.py ─→ cve_stats.py ─→ bootloader_cve_db
cvelistV5 ─────────────┘
oss-bootloaders ───────┬─ extract_vuln_commits.py ────────→ bootloader_vuln_commits
                       └─ generate_table.py ──────────────→ oss-bootloaders/table.md
dblp ──────────────────── collect_papers.py ──────────────→ PAPERS.md

refresh_dataset.py wraps the first two rows: stage → diff → review → --apply
validate_dataset.py checks the result
```

## Where these came from

The dataset was originally built by four scripts across three places:

| Stage | Original | Status |
|---|---|---|
| CVE mining and classification | `collect_cves.py` in `BreakingBoot/cvedb` (`bootloaderdb`) | private repo — reimplemented as `classify_cves.py` |
| CVE split and statistics | `postprocess_bootloader_cves.py`, same private repo | private repo — reimplemented as `cve_stats.py` |
| Commit mining | `bootloader_vuln_commits/extract_cve_commits.py` | public — improved as `extract_vuln_commits.py` |
| Inventory table | `oss-bootloaders/generate_table.py` | public — improved as `generate_table.py` |
| Literature search | [top4grep](https://github.com/Kyle-Kyle/top4grep) | external — extended as `collect_papers.py` |

**Fidelity.** Replaying the reimplemented rules over the published dataset
reproduces every committed `type<N>-keyword-breakdown.json` exactly (734 / 301 /
122 CVEs, zero differences), and `cve_stats.py --no-normalize` reproduces the
published `stats.md` counts. Verify with
`python3 validate_dataset.py --root .. --check classification`.

Fourteen defects were found in the original tools and data and fixed here, each
measured against the committed data, alongside performance and path-independence
fixes.
The largest are a `previous_commit` field that pointed at the *next newer*
commit rather than the parent, substring keyword matching that made 34% of the
mined commits false positives, and CWE labels assigned by fuzzy string
similarity.
