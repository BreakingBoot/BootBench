# `generate_wiki.py`

Generates [`wiki/`](../../wiki/): a page per bootloader and a page per analysis
tool.

```bash
python3 generate_wiki.py --root .. --output ../wiki          # for the repo
python3 generate_wiki.py --root .. --output /tmp/w --flat    # for a GitHub wiki
```

`--flat` writes every page at the top level with a prefix
(`Bootloaders-u-boot.md`) and rewrites links to match, because a GitHub wiki
addresses pages by filename. `scripts/publish-wiki.sh` uses it.

## Split between generated and curated

**Generated from the datasets:** CVE counts, attributed CWEs, attack surfaces,
detected security mechanisms, commit history, linked reproducible
vulnerabilities, tool status and verified runs. A page cannot drift from the
data it describes, and regenerating after a refresh updates every page.

**Curated in [`wiki_content.py`](../wiki_content.py):** what a bootloader
actually does at boot, and why that places it in Type 1, 2 or 3. That judgement
cannot be generated — it is the part a reader most needs and the part a script
cannot infer.

A test fails if a corpus bootloader has no prose, or if prose exists for a
bootloader that is no longer in the corpus.

## Pages

| Page | Contents |
|---|---|
| `Home` | Index and corpus summary |
| `Bootloader-Types` | What Type 1/2/3 mean, the test used, and where classification is arguable |
| `Attack-Surfaces` | The six surfaces, what reaches each, and the observed distribution |
| `Security-Mechanisms` | What the corpus defends itself with, and how to read a detection |
| `Bootloaders` | Index of all 62, grouped by type |
| `bootloaders/<name>` | One per bootloader |
| `Tools` | Index of all 24 analysis tools |
| `tools/<name>` | One per tool, with a walkthrough |

## Adding a bootloader

Add it to `oss-bootloaders` with `scripts/add-bootloaders.sh`, write its three
curated fields in `wiki_content.py`, and regenerate. The third field is the
important one: it should answer where the bootloader starts and what it hands
off to, because that is what the taxonomy turns on.
