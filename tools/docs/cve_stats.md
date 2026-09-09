# `cve_stats.py`

Splits a `<type>-results.json` into one file per CVE and renders the
`stats.md` table. The second half of the `bootloader_cve_db` pipeline.

## Run it

```bash
python3 cve_stats.py --input results/type1-results.json \
                     --output ../bootloader_cve_db/type1/cves \
                     --stats  ../bootloader_cve_db/type1/stats.md \
                     --source-dir ./cvelistV5
```

| Flag | Purpose |
|---|---|
| `--input FILE` | A `<type>-results.json`. Required. |
| `--output DIR` | Write one `<CVE-ID>.json` per CVE here. |
| `--stats FILE` | Write the markdown table here. Prints to stdout if omitted. |
| `--source-dir DIR` | Resolve records by CVE ID from here. See below. |
| `--keep` | Do not delete `--output` before writing. |
| `--no-normalize` | Group `vuln_type` verbatim, reproducing the original grouping. |

## `--source-dir` is usually needed

`results.json` stores the absolute path each record was read from. On the
published data those point into the CI runner's workspace
(`/home/.../actions-runner/_work/...`) and resolve nowhere else, so `--output`
silently copies nothing. `--source-dir` takes a cvelistV5 checkout — or an
existing `cves/` directory — and resolves by CVE ID instead.

## What it fixes

**Vendor share no longer exceeds 100%.** The published tables report `Intel
(125.00%)`, `Dell (200.00%)`, `Dell (400.00%)`. Those numbers are reproduced
exactly by dividing the leading vendor's count by the *number of distinct
vendors* instead of the vendor total — a `len(counter)` where
`sum(counter.values())` was meant. Now reported as
`Dell (68 of 85 attributed, 80.00%)` so the denominator is visible.

**Rows sum to the stated total.** In every published `stats.md` the
vulnerability-type rows fall short of the total in the same file: 609 vs 734,
203 vs 301, 59 vs 122. This emits the full distribution.

**`vuln_type` variants are merged.** `CWE-20: Improper Input Validation` and
`CWE-20 Improper Input Validation` were counted separately, splitting CWE-20
into 69 + 16. Normalising case and the CWE prefix merges them to 85. Pass
`--no-normalize` to reproduce the original grouping — which it does exactly.
