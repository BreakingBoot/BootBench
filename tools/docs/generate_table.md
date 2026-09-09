# `generate_table.py`

Renders the bootloader inventory table for `oss-bootloaders/README.md`.

## Run it

```bash
python3 generate_table.py --root ../oss-bootloaders --output ../oss-bootloaders/table.md
```

| Flag | Purpose |
|---|---|
| `--root DIR` | Directory containing `type1/ type2/ type3/`. Default cwd. |
| `--output FILE` | Markdown file to write. Default `table.md`. Parent directories are created. |

## Output

| Type | Bootloader | Commits | First Commit | Latest Commit |
|------|-----------|---------|--------------|---------------|
| Type 1 - Firmware | [coreboot](https://github.com/coreboot/coreboot) | 52341 | 2003-05-01 | 2025-08-14 |

Upstream URLs come from `.gitmodules`, so the table links to each project rather
than depending on a hand-maintained list in the README. SSH remotes are
rewritten to browsable HTTPS.

## Uninitialised submodules

Commit data requires the nested submodules to be checked out:

```bash
git -C ../oss-bootloaders submodule update --init --recursive
```

Without that the table says `not initialized` and the tool warns on stderr. The
original printed `N/A`, which was indistinguishable from a repository with no
commits — so a table built from a non-recursive clone looked like real data.

Note `type2/open-iscsi` is declared in `.gitmodules` but has no directory, so it
appears in neither the table nor the mined commit data.
