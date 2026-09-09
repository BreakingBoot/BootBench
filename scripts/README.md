# Scripts

Operator scripts. The tools in [`../tools/`](../tools/) do the work; these wrap
them into the things you actually want to run.

There is no CI in any BootBench repository — these scripts replace it. Nothing
here commits or pushes; each one prints the git commands to publish what it
changed.

| Script | Does |
|---|---|
| [`run-all-tools.sh`](run-all-tools.sh) | Run every tool against a scratch directory and report what each produced. Read-only. |
| [`update-oss-bootloaders.sh`](update-oss-bootloaders.sh) | Regenerate `oss-bootloaders/table.md`. |
| [`update-bootloader-cve-db.sh`](update-bootloader-cve-db.sh) | Refresh the CVE database from cvelistV5, with a diff to review first. |
| [`update-bootloader-vuln-commits.sh`](update-bootloader-vuln-commits.sh) | Re-mine the bootloader histories for vulnerability fixes. |
| [`update-papers.sh`](update-papers.sh) | Re-run the literature search, regenerating `PAPERS.md`. |
| [`add-bootloaders.sh`](add-bootloaders.sh) | Add the bootloaders in `tools/new_bootloaders.json` to `oss-bootloaders`. |
| [`add-analysis-tools.sh`](add-analysis-tools.sh) | Add the tools in `tools/analysis_tools.json` under `analysis-tools/`. |
| [`analysis/run-tool.sh`](analysis/run-tool.sh) | Run one of the analysis tools against a bootloader. See [`analysis/`](analysis/). |

Common flags: `-y` skips the confirmation prompt, `--dry-run` on the `add-*`
scripts lists what would be added, `--stage-only` on the `update-*` refresh
scripts stops after staging.

## Running the analysis tools

`scripts/` builds and checks the *dataset*. Running the *analysis tools* against
a bootloader is [`analysis/run-tool.sh`](analysis/):

```bash
./scripts/analysis/run-tool.sh --list          # what runs, what is blocked, and why
./scripts/analysis/run-tool.sh codeql kexec-tools
```

Everything there works through docker, so the host needs no toolchain. See
[`analysis/README.md`](analysis/README.md).

## Checking things

```bash
./scripts/run-all-tools.sh                    # everything, into a scratch dir
./scripts/run-all-tools.sh --skip-network     # no dblp query
```

Tools that need a submodule you have not checked out are skipped with a note,
not failed. Dataset validation findings are reported but do not fail the run —
they are data problems, not tool problems.

## Refreshing data

Each refresh stages outside the submodule, prints a diff, and asks before
writing:

```bash
./scripts/update-bootloader-cve-db.sh                  # clones cvelistV5 if needed
./scripts/update-bootloader-cve-db.sh --stage-only     # diff, then stop
```

Read the `RELABELLED` section before answering yes. It lists CVEs that changed
bootloader type, which is the dataset's central claim about a CVE and the thing
a keyword-list edit can silently change.

Commit mining needs the full corpus checked out, which is large:

```bash
git -C oss-bootloaders submodule update --init --recursive
./scripts/update-bootloader-vuln-commits.sh
```

## Adding to the corpus

Both `add-*` scripts are driven by a JSON manifest, so adding something means
editing the manifest and re-running:

```bash
./scripts/add-bootloaders.sh --dry-run        # what would be added
./scripts/add-bootloaders.sh                  # add them
./scripts/add-bootloaders.sh --only oreboot   # just one
```

`add-bootloaders.sh` regenerates `table.md` afterwards. After
`add-analysis-tools.sh`, regenerate the index:

```bash
python3 tools/generate_tools_table.py --output analysis-tools/README.md
```

## A note on `update-oss-bootloaders.sh`

It writes `table.md` and stops. The retired CI also concatenated
`description.md + table.md` into `README.md`, which would replace the curated
bootloader list with empty sections while `description.md` is a stub. The script
refuses to do that until `description.md` has real prose in it.
