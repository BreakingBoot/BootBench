# `generate_tools_table.py`

Renders [`analysis-tools/README.md`](../../analysis-tools/README.md) from
[`analysis_tools.json`](../analysis_tools.json).

```bash
python3 generate_tools_table.py --output ../analysis-tools/README.md
```

| Flag | Purpose |
|---|---|
| `--manifest FILE` | Tool manifest. Default `tools/analysis_tools.json`. |
| `--output FILE` | Markdown file to write. Required. Parent directories are created. |

The manifest is the source of truth for the tool collection: it records where
each tool lives, what it does, why it is in BootBench, and its language, star
count and last push at the time it was added. The same file drives
[`scripts/add-analysis-tools.sh`](../../scripts/add-analysis-tools.sh), so the
README cannot drift from the submodules that are actually checked in.

To add a tool: append an entry to the manifest, run the add script, then
regenerate the README.

Star counts and last-push dates are snapshots taken when the entry was added.
They are there to show whether a tool is maintained, not to be exact — re-run
the verification if you need current numbers.
