# What was wrong, and what changed

Every claim here was measured against the committed dataset, not inferred from
reading the code. [`validate_dataset.py`](../validate_dataset.py) re-derives
all of them, and [`test_tools.py`](../test_tools.py) has a regression test for
each behavioural fix.

## 1. `previous_commit` pointed at the wrong commit

`extract_cve_commits.py` filled `previous_commit` from the preceding iteration
of its `git log` walk. `git log` is newest-first, so the field held the *next
newer* commit, not the parent — and its name says otherwise.

For a vulnerability dataset this is the field that matters most: when a commit
is the fix, its parent is the last revision that still contains the bug, which
is what a pre-/post-patch evaluation needs. Of the 548 records where the link
can be checked against another record in the same file, **467 point forwards in
time** and 81 backwards (the 81 are author-date vs. topological-order artifacts).

`extract_vuln_commits.py` reads parents from git itself (`%P`) and emits
`parent` (first parent) and `parents` (all, so merges are not silently
flattened). Verified against `git rev-list --parents` on a live `shim` clone:
38 of 38 records exact.

The field is **renamed, not repaired in place**. Keeping the old name with
corrected semantics would silently change the meaning of data other people have
already parsed; a rename makes the change visible.

## 2. Keyword matching ignored its own word boundaries

The script compiled word-bounded patterns into `VULN_PATTERNS`, then never used
them — the actual test was `any(kw in lower_msg for kw in VULNERABILITY_KEYWORDS)`,
a bare substring match. Re-running both matchers over the 3,377 published
`vulnerability` commits:

| Matcher | Commits matched |
|---|---|
| Substring (what shipped) | 3,377 |
| Word-bounded | 2,275 (**−1,102, 32.6%**) |

The 1,102 difference is noise: "TODOs", "msdos", "FreeDOS", "kudos".

Word boundaries alone overcorrect, though: they also drop "Prevent buffer
overflows", "Fix race conditions" and "caused by NULL pointers", which are real
fixes the substring matcher did catch. Measured against six freshly cloned
bootloader repositories, that cost 9 genuine findings. Commit-message keywords
therefore accept a trailing `s`/`es` on the final word — tight enough to still
reject "exploitation" for `exploit` and "TODOs" for `dos`. Type classification
deliberately does **not** do this, since it must keep reproducing the published
keyword breakdown exactly; `compile_keywords(..., allow_plural=True)` is opt-in
and covered by a regression test in both directions.

## 3. The `dos` keyword matched DOS the operating system

Word boundaries alone do not save this one. `\bdos\b` still matches 267 of the
published commits. Of those, 255 do not also match a case-sensitive `\bDoS\b`,
and every surface form in them — `DOS` (283 occurrences), `dos` (65), `Dos` (6)
— is DOS the operating system, not denial of service: "pe: tighten validity
checks of DOS and PE headers", "rules: add /dev/disk/by-partuuid symlinks also
for dos partition table", "bootctl: tweak DOS header magic check", and a sample
directory called `Dos`.

The bare acronym is dropped. Denial of service is matched by the spelled-out
phrase plus a case-sensitive `\bDoS\b`, which is how the security acronym is
written.

Taken together — word boundaries, plural tolerance, no bare `dos`, and
`vulnerable` added — the matcher retains 2,226 of the 3,377 published
keyword-matched commits and rejects **1,151 (34.1%)** as false positives.

`vulnerable` is the loosest keyword in the set: 24 commits match on it alone,
and roughly half of those are incidental ("it is after all not vulnerable to
reuse"). It earns its place by catching real security work that nothing else
matches — SBAT revocations of vulnerable boot managers, firmware
anti-rollback — and because every record now carries `matched_keywords`, a
consumer that wants stricter precision can drop commits matched only by it in
one line.

## 4. CWE tagging was fuzzy and wrong

CWE labels came from `rapidfuzz.fuzz.token_set_ratio(message, cwe_name)` at
threshold 90. `token_set_ratio` scores 100 whenever one string's token set is a
subset of the other's, so any commit message containing a short CWE name's words
— anywhere, in any order — is a perfect match. Actual labels in the published
data:

| Commit message | CWE it was tagged with |
|---|---|
| `Bump version to 15.8` | CWE-680 Integer Overflow to Buffer Overflow |
| `roms: only support SeaBIOS/SeaGRUB on x86` | CWE-260 Password in Configuration File |
| `pflash: Clean up makefiles and resolve build race` | CWE-114 Process Control |
| `A number of cleanups for 440BX raminit code.` | CWE-1041 Use of Redundant Code |
| `scripts/dtc: Update to upstream version v1.7.0` | CWE-1041 Use of Redundant Code |

Tagging is now an explicit alias table (`CWE_ALIASES`) of phrases that actually
appear in fix commits, matched with word boundaries. This trades recall for
precision and makes recall extensible by adding aliases — a judgement call a
similarity threshold cannot express. It also drops the RapidFuzz dependency.

## 5. Absence was used to mean "clean"

`extract_cve_commits.py` returned `None` for a repository with no findings, so
it wrote a JSON file but no `summary.json` row. The published summary has 32
entries for 48 mined repositories; the 16 missing ones are indistinguishable
from repositories that were never scanned.

Every scanned repository now gets a summary row, including a `commits_scanned`
count, so a zero is positive evidence of a clean scan.

## 6. Failures were indistinguishable from clean results

A repository whose `git log` failed produced the same empty JSON as one with
genuinely no findings. Failures now produce an explicit `"error"` row.

## 7. Non-repositories were scanned

The loop scanned every subdirectory of a `type*/` folder. The published dataset
still contains `type1/Download.json`, the residue of a directory that was never
a git repository. Directories are now checked for `.git` and skipped with a
notice.

## 8. Statistics rows did not sum to their own totals

In every committed `stats.md`, the vulnerability-type rows are short of the
total the same file states:

| File | Rows sum to | Table states | Unaccounted |
|---|---|---|---|
| `type1/stats.md` | 609 | 734 | 125 (17%) |
| `type2/stats.md` | 203 | 301 | 98 (33%) |
| `type3/stats.md` | 59 | 122 | 63 (52%) |

The year breakdowns in the same files do sum correctly. `cve_stats.py` emits the
full distribution.

## 9. Vendor share exceeded 100%

The published tables report `Intel (125.00%)`, `Dell (200.00%)`, `Dell
(400.00%)`. The numbers are reproduced exactly by dividing the leading vendor's
count by the *number of distinct vendors* rather than by the vendor total — a
`len(counter)` where `sum(counter.values())` was meant:

```
escalation of privilege:  Intel 5 / 4 distinct vendors = 125.00%
cwe-20:                   Dell  2 / 1 distinct vendor  = 200.00%
cwe-119:                  Dell  4 / 1 distinct vendor  = 400.00%
denial of service:        HP    2 / 9 distinct vendors =  22.22%
```

Fixed, and reported as `Dell (68 of 85 attributed, 80.00%)` so the denominator
is visible.

## 10. `vuln_type` was never normalised

`CWE-20: Improper Input Validation` and `CWE-20 Improper Input Validation` were
counted as different classes, splitting CWE-20 into 69 + 16. Normalising case
and the CWE prefix merges them (85 for CWE-20, 43 for CWE-119). Pass
`--no-normalize` to reproduce the original grouping.

## 11. Withdrawn CVEs are still counted

56 record files in the dataset — 55 distinct CVEs, 4.8% of the corpus — have
been **rejected upstream**: "DO NOT USE THIS CANDIDATE NUMBER. ... The CNA or
individual who requested this candidate did not associate it with any
vulnerability." Their `cves/*.json` records carry no description at all, only a
rejection reason, yet `results.json` still holds the pre-rejection text and they
are still counted in every total and keyword breakdown.

`classify_cves.py` skips them by default and reports the count. Because a
rejected record has no description, `--include-rejected` cannot classify them
either — it exists to audit a dataset that already contains them.

## 12. Two CVEs are counted under two types

`CVE-2014-9233` and `CVE-2014-9796` appear under both Type 2 and Type 3, so the
per-type totals sum to 1,157 while covering **1,155 distinct CVEs**. Both match
`aboot` (Type 2) and `boot image` (Type 3).

The cause is in the keyword lists: the Type 3 exclude list was built from the
Type 1 include and exclude lists rather than from Type 2's *include* list, so
the three keywords unique to Type 2's include list — `aboot`,
`android bootloader`, `pxelinux` — are never excluded from Type 3.
`classify_cves.py --report-overlaps` writes out every CVE that satisfies more
than one type's rules, which is the set to review when tuning the lists.

## 13. The CVE workflow does not run on a schedule

`bootloader_cve_db/README.md` states the database is "automatically run once a
week", but the workflow's triggers are `push` to the `test` branch and
`workflow_dispatch` — there is no `schedule:` block, so nothing runs weekly. The
data is a snapshot from the last manual dispatch.

## 14. `generate_table.py`: silent git failures and unusable output

* `subprocess.run` was called without `check=True`, so the `except
  subprocess.CalledProcessError` handler was unreachable — every git failure
  became the string `N/A`.
* An uninitialised submodule also rendered as `N/A`, so a table built from a
  non-recursive clone was indistinguishable from real data. All 46 present
  submodules are currently uninitialised, so this is the normal case, not an
  edge case. It now says `not initialized` and warns on stderr.
* Upstream URLs are read from `.gitmodules` instead of being maintained by hand
  in the README, and commit counts and first-commit dates are included.
* The header said `Bootlaoder`.

## 15. CI still invokes the original tools

Nothing in this directory is wired into the submodules' GitHub Actions. Both
workflows still call the code these tools replace:

* `bootloader_cve_db/.github/workflows/main.yml` clones the private
  `BreakingBoot/cvedb` repo and runs `collect_cves.py` and
  `postprocess_bootloader_cves.py`, with the keyword lists inline as shell
  arguments.
* `oss-bootloaders/.github/workflows/main.yml` runs the submodule's own
  `generate_table.py`.

A `workflow_dispatch` on either would regenerate the data with the original
code, reintroducing the vendor percentages over 100%, the statistics rows that
do not sum, the `N/A` for uninitialised submodules, and the `Bootlaoder` header
typo.

Rewiring them is a change *inside* the submodules, so it is left alone here.
The replacement invocations are:

```yaml
# bootloader_cve_db
python3 tools/classify_cves.py --cvelist ./cvelistV5 --output results
python3 tools/cve_stats.py --input results/type1-results.json         --output type1/cves --stats type1/stats.md --source-dir ./cvelistV5   # and type2, type3

# oss-bootloaders
python3 tools/generate_table.py --root . --output table.md
```

## 16. Everything is now parallel and path-independent

The commit miner ran serially over 48 repositories while comparing every commit
message against 669 CWE names in a Python loop — quadratic work on histories
like coreboot's. Repository scans now run across processes (`--jobs`), and CWE
matching is a bounded set of precompiled patterns.

`load_cwes()` also ran at import time against the relative path `cwes.json`, so
running the script from any other directory silently disabled CWE matching with
only a warning. Paths are now resolved relative to the script.

# Known coverage gaps in the current dataset

Reported by `validate_dataset.py --check coverage`:

* **`type2/open-iscsi`** is declared in `oss-bootloaders/.gitmodules` but has no
  directory on disk, which is why it was never mined.
* **`type1/Download.json`** and **`type3/harmony3.json`** are mined outputs with
  no corresponding submodule.
* **16 of 48** mined repositories are missing from `summary.json` (item 5).
* **55 withdrawn CVEs** and **2 double-counted CVEs** remain in
  `bootloader_cve_db` (items 11 and 12); `validate_dataset.py --check records`
  lists them.

These are recorded, not silently repaired: fixing them means re-mining, which
changes published dataset numbers and is the maintainer's call.
