# `extract_vuln_commits.py`

Mines bootloader git histories for commits that reference a CVE or match a
vulnerability keyword. Produces `bootloader_vuln_commits`.

## Run it

```bash
git -C ../oss-bootloaders submodule update --init --recursive   # large
python3 extract_vuln_commits.py ../oss-bootloaders \
        --output ../bootloader_vuln_commits --jobs 8
```

About 21,000 commits across six repositories in ~2 seconds on 6 workers.

| Flag | Purpose |
|---|---|
| *(positional)* | Directory containing `type1/ type2/ type3/` repository trees. |
| `--output DIR`, `-o` | Output directory. Default `output/`. |
| `--jobs N`, `-j` | Parallel repository scans. Default `min(8, CPU count)`. |
| `--since DATE` | Only commits after this date, e.g. `2015-01-01`. Git's `--since` is strictly exclusive at the boundary. |

## Output

`<type>/<repo>.json`, split into `CVEs` (commits naming a CVE) and
`vulnerability` (keyword matches only):

```json
{"commit": "3e1394e8...", "parent": "470a8cd1...", "parents": ["470a8cd1..."],
 "date": "2024-04-09T18:55:12+02:00", "commit_date": "...",
 "message": "...", "cve_ids": ["CVE-2023-40547"],
 "matched_keywords": ["buffer overflow"],
 "CWE_matches": [{"CWE-ID": "787", "Name": "Out-of-bounds Write", "matched": "..."}]}
```

`summary.json` carries per-repository counts plus `commits_scanned`, with a row
for **every** repository scanned — a zero is evidence of a clean scan.

## Field changes from the original

**`parent`/`parents` replace `previous_commit`.** The old field was filled from
the previous step of a newest-first `git log` walk, so it pointed at the *next
newer* commit: on the published data, 467 of 548 checkable links point forwards
in time. For a vulnerability dataset this is the field that matters — the parent
is the last revision that still contains the bug. This tool reads `%P` from git.

The field is renamed rather than repaired in place, so the change is visible to
anything already parsing the old name.

**`cve_ids`** lists every CVE in the message, not just the fact that one exists.
One shim commit names 21.

**`matched_keywords`** records why each commit was included, so any entry can be
traced back to the rule that put it there.

## Matching

Word-bounded, plural-tolerant (`buffer overflows` counts), case-sensitive for
the `DoS` acronym. The bare keyword `dos` is gone — it matched 267 commits, all
of them about DOS the operating system. CWE tagging is an explicit phrase table,
not fuzzy similarity.

## Verification

Over six freshly cloned bootloaders, all 182 emitted parent links match
`git rev-list --parents` exactly, and every one is confirmed a true ancestor via
`git merge-base --is-ancestor`.
