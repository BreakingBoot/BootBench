# `link_cves_to_commits.py`

Joins the two halves of BootBench: for every CVE in `bootloader_cve_db`, finds
the commits in `bootloader_vuln_commits` that name it, and records each
commit's **parent** — the last revision that still contains the bug.

That chain is the benchmark's central workflow, and nothing in the dataset
stored it before: the CVE database and the commit database share no key.

## Run it

```bash
python3 link_cves_to_commits.py --root .. \
    --output ../bootloader_vuln_commits/cve-commit-links.json \
    --markdown ../bootloader_vuln_commits/LINKS.md
```

Re-run after any refresh — `refresh_dataset.py` does not do it for you.

| Flag | Purpose |
|---|---|
| `--root DIR` | BootBench checkout root. |
| `--output FILE` | JSON index. Default `bootloader_vuln_commits/cve-commit-links.json`. |
| `--markdown FILE` | Also write a coverage summary. |

## Output

```json
{"links": {"CVE-2022-28737": {
    "type": "type2", "vuln_type": "...", "vendor": "...",
    "fixes": [{"repo": "type2/shim",
               "commit": "159151b66490...",
               "parent": "9a09faf390ee...",
               "subject": "Also avoid CVE-2022-28737 in verify_image()"}]}}}
```

To reproduce that bug: `git -C oss-bootloaders/type2/shim checkout <parent>`.

## Coverage, and why it is what it is

78 of 1,432 CVEs resolve to a fixing commit. That is not an error. A CVE links
only when **both** conditions hold: the fix landed in a bootloader that is in
the corpus, and the commit message names the CVE. Vendor firmware fixes, silent
fixes, and fixes predating a submodule's pinned revision all fall outside.

The tool reports both failure directions, because each says something
different:

* **Unlinked CVEs** (1,354) — in the database, no fixing commit found.
* **Orphan references** (120) — named in bootloader commits but absent from the
  database. Each is either a CVE the keyword classifier missed or a
  non-bootloader CVE mentioned in passing, and they are worth reviewing before
  quoting the CVE totals as complete.

The orphan list is the more useful of the two: it is a concrete, bounded set of
candidates for improving the classifier, derived from evidence rather than from
guessing at keywords.
