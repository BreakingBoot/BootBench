# `refresh_dataset.py`

Regenerates the dataset into a staging directory and reports what would change.
**Nothing is written to the submodules without `--apply`.**

A refresh changes published numbers that the paper cites, so the diff — the
label diff especially — is the thing to read.

## Run it

```bash
# 1. stage a CVE refresh and read the diff
python3 refresh_dataset.py --stage cves --cvelist ~/cvelistV5 --staging /tmp/refresh

# 2. stage a commit refresh
python3 refresh_dataset.py --stage commits --staging /tmp/refresh

# 3. only after confirming the labels, apply
python3 refresh_dataset.py --stage cves --cvelist ~/cvelistV5 \
        --staging /tmp/refresh --apply
```

| Flag | Purpose |
|---|---|
| `--stage cves\|commits\|table` | Which part to regenerate. Required. |
| `--staging DIR` | Where to build it. Refused if inside a submodule. Required. |
| `--cvelist PATH` | cvelistV5 checkout. Required for `--stage cves`. |
| `--root DIR` | BootBench checkout root. Default `..`. |
| `--apply` | Copy the staged refresh into the submodules. Runs `validate_dataset.py` first and refuses if it fails. |

## What the diff shows

```
=== CVE diff ===
  live:    1155 distinct CVEs
  staged:  1100 distinct CVEs

  added:       0
  removed:     55
  RELABELLED:  1   <-- confirm these by hand
      ~ CVE-2014-9796  type3 -> type2

  keyword attribution:
      type1: 5 keyword(s) changed count
          'bios': 367 -> 345
```

**RELABELLED** is the section that matters. The bootloader type is the dataset's
central claim about a CVE, and a keyword-list edit can move CVEs between types
without changing any count you would otherwise notice. Confirm each one.

**Keyword attribution** shows CVEs that stayed in their type but were credited
to a different keyword — usually harmless, but it is how a reordered keyword
list announces itself.

## After applying

`--apply` writes into the submodule working trees but does not commit. Commit
from inside each submodule, then update the pointer in the superproject:

```bash
git -C bootloader_cve_db add -A && git -C bootloader_cve_db commit -m "Refresh CVEs"
git -C bootloader_cve_db push
git add bootloader_cve_db && git commit -m "Bump bootloader_cve_db"
```
