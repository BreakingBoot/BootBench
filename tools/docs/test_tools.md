# `test_tools.py`

The test suite for everything in `tools/`.

```bash
python3 test_tools.py        # 47 tests
python3 test_tools.py -v     # per-test detail
```

**Hermetic.** The git-dependent tests build throwaway repositories with known
history — including a merge commit — in a temp directory, so no network access
and no submodule checkout are needed. Tests that compare against the published
dataset skip themselves if the data submodules are not initialised.

## What it covers

| Group | Asserts |
|---|---|
| `TestClassificationFidelity` | The keyword rules reproduce the published breakdown; exclude lists reject none of their own CVEs; first-match ordering is significant; classification is *not* plural-tolerant. |
| `TestClassifyCvesEndToEnd` | The script assigns types correctly, skips withdrawn CVEs, reports vendor as `n/a` rather than guessing, and flags multi-type overlaps. |
| `TestMinerParents` | Parents match `git rev-list --parents`, are ancestors rather than descendants, and merges keep every parent. |
| `TestMinerMatching` | "TODOs" and "DOS header" are not vulnerabilities; `DoS` and plural forms are; CVE IDs are extracted; CWE tagging needs an explicit phrase. |
| `TestMinerRobustness` | A message containing `---END---` does not split a record; clean repos still get a summary row; non-repositories are skipped; `--since` narrows the scan. |
| `TestCollectPapers` | Boot papers match as core; FHE/ML "bootstrap" is rejected; contribution rules assign the right category; a top4grep database can be read. |
| `TestCveStats` | Vendor share never exceeds 100%; rows sum to the total; `--no-normalize` reproduces published counts. |
| `TestGenerateTable` | Header typo is gone; uninitialised submodules are reported as such; output directories are created; SSH URLs are rewritten. |

## Adding to it

Two conventions worth keeping:

* **Assert the bug, not just the fix.** Several tests name the exact false
  positive that shipped (`TODOs`, `Bump version to 15.8`), so a future
  loosening of the rules fails loudly.
* **Assert both directions of a deliberate asymmetry.** Plural tolerance is on
  for commit messages and off for CVE classification, and there is a test for
  each, because turning it on for classification would silently change the
  published breakdown.
