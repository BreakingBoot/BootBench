# `classify_cves.py`

Scans a [CVEProject/cvelistV5](https://github.com/CVEProject/cvelistV5) checkout,
keeps the CVEs whose description names a bootloader, and assigns each one a
bootloader type. Produces `bootloader_cve_db`.

## Run it

```bash
git clone --depth 1 https://github.com/CVEProject/cvelistV5.git
python3 classify_cves.py --cvelist ./cvelistV5 --output ./results
```

~387,000 records in about a minute on 8 workers.

| Flag | Purpose |
|---|---|
| `--cvelist PATH` | cvelistV5 checkout. Required. |
| `--output DIR` | Where to write results. Default `results/`. |
| `--type type1\|type2\|type3` | Restrict to one type. Repeatable, default all three. |
| `--jobs N` | Worker processes. Default `min(8, CPU count)`. |
| `--include-rejected` | Keep CVEs withdrawn upstream. See caveat below. |
| `--report-overlaps` | Also write `type-overlaps.json`: CVEs satisfying more than one type's rules. |

## Output

`<type>-results.json` — index keyed by CVE ID:

```json
{"CVE-2015-0949": {
  "cve_id": "...", "description": "...", "published_date": "...",
  "vendor": "Dell", "vuln_type": "Other", "file_path": "/path/to/record.json"}}
```

`<type>-keyword-breakdown.json` — how many CVEs each keyword accounted for.

## How classification works

Include keywords minus exclude keywords, matched with word boundaries, **first
match in list order wins**. The lists live in
[`bootbench_keywords.py`](../bootbench_keywords.py) (`BOOTLOADER_TYPES`).

Order is significant — it decides which keyword a multi-keyword CVE is credited
to — so after editing a list, re-run:

```bash
python3 validate_dataset.py --root .. --check classification
```

Types are checked in order and the first match wins, so a CVE satisfying two
types lands in the lower-numbered one. `--report-overlaps` tells you which.

## Caveats

**Withdrawn CVEs are skipped.** A rejected record ("DO NOT USE THIS CANDIDATE
NUMBER") has no description left to classify. `--include-rejected` exists to
audit a dataset that already contains them; it cannot actually classify them.

**`vendor` is not normalised.** The original private tool emitted a normalised
vendor — a record whose only vendor string is `n/a` and whose description says
"SuperMicro" was published as `Supermicro` — using a lookup table that was never
released. This tool reports what the record says and marks the rest `n/a`.

## Fidelity

Replaying its rules over the published dataset reproduces every committed
`type<N>-keyword-breakdown.json` exactly: 734 / 301 / 122 CVEs, zero
keyword-count differences, and no type's exclude list rejects any of its own
published CVEs.

Run end to end against a full cvelistV5 checkout, it re-derives 1,100 of the
1,155 distinct published CVEs. The 55 it misses are exactly the 55 withdrawn
upstream — zero unexplained misses, and no CVE lands in a different type.
