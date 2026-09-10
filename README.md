# BootBench

BootBench is the dataset behind *SoK: All You Ever Wanted to Know About
Bootloader Security but Were Afraid to Ask*, by Connor Glosner and Aravind
Machiry (Purdue University), IEEE S&P 2026. It pairs open-source bootloader
source trees with the vulnerabilities recorded against them, so that bootloader
analysis tools can be evaluated against real bugs in real bootloaders.

Paper: [PDF](https://machiry.github.io/files/soksp2026.pdf) ·
[DOI](https://doi.org/10.1109/SP63933.2026.00163)

## What's here

Three submodules hold the data. `tools/` builds it.

**[`oss-bootloaders`](https://github.com/BreakingBoot/oss-bootloaders)** — the
corpus. 63 bootloader repositories pinned as nested submodules and grouped by
type (14 Type 1, 28 Type 2, 21 Type 3). Pointers only, nothing vendored. The
paper studied 47 of these; the rest were added afterwards and have no mined data
yet.

**[`bootloader_cve_db`](https://github.com/BreakingBoot/bootloader_cve_db)** —
1,432 CVEs mined from the [CVE Project](https://github.com/CVEProject/cvelistV5)
records and assigned a bootloader type by keyword. Each type directory holds the
full upstream record per CVE, an index (`type<N>-results.json`), the keyword
breakdown that produced the classification, and generated statistics.

**[`bootloader_vuln_commits`](https://github.com/BreakingBoot/bootloader_vuln_commits)** —
3,514 commit records mined from those repositories at their pinned revisions:
390 that name a CVE and 3,124 matched on vulnerability keywords. That is down
from 3,656 because re-mining removed 1,151 false positives — 95% of them the
bare `dos` keyword matching "glados", "TODOs" and "DOS header" — while adding
843 from 17 newly-mined bootloaders. These are the
security fixes that never got a CVE, which is most of them.
[`cve-commit-links.json`](https://github.com/BreakingBoot/bootloader_vuln_commits/blob/main/cve-commit-links.json)
joins the two halves: 78 CVEs resolve to a fixing commit and to the parent
revision that still contains the bug.

**[`analysis-tools/`](analysis-tools/)** — 24 bootloader and firmware analysis
tools as submodules, grouped by what they do: static analysis, fuzzing and
rehosting, image inspection, platform assessment. These are what BootBench
exists to evaluate.

**[`tools/`](tools/)** — the collection, classification and validation tools,
one document per tool in [`tools/docs/`](tools/docs/).
[`tools/OVERVIEW.md`](tools/OVERVIEW.md) is the table of which analysis tools
work and which bootloaders each applies to.

**[`scripts/`](scripts/)** — the scripts you run: refresh a submodule, add to
the corpus, and [`scripts/analysis/`](scripts/analysis/) to run an analysis tool
against a bootloader. There is no CI in any BootBench repository; these replace
it, and none of them commits or pushes.

**[`PAPERS.md`](PAPERS.md)** — bootloader papers from the eight venues the SoK
surveyed, grouped by contribution.

## Bootloader types

Everything is organised by the paper's three-way split, by how a bootloader
initialises and hands off:

**Type 1, firmware bootloader.** Boots from hardware and presents a
hardware-agnostic interface to whatever runs next. UEFI/EDK-II, SeaBIOS,
coreboot.

**Type 2, OS bootloader.** Boots from an already-initialised system and prepares
for an OS. GRUB2, shim, Windows Boot Manager.

**Type 3, monolithic bootloader.** Both jobs at once — hardware straight to OS,
no handoff. Hardware-specific, common in embedded systems. U-Boot, MCUboot, ARM
Trusted Firmware.

Types 1 and 2 chained together are staged booting, typical of desktops, servers
and phones. Type 3 is monolithic booting, typical of IoT and MCU devices. The
paper defines six attack surfaces over these types: invasive hardware, external
hardware, remote access, persistent data sources, post-boot features and
boot-time features.

## Getting started

```bash
git clone https://github.com/BreakingBoot/BootBench.git
cd BootBench
git submodule update --init oss-bootloaders bootloader_cve_db bootloader_vuln_commits
./scripts/run-all-tools.sh
```

The three data submodules are small. Two other groups are large and optional:

```bash
git -C oss-bootloaders submodule update --init --recursive   # bootloader sources
git submodule update --init --recursive analysis-tools       # the analysis tools
git -C oss-bootloaders submodule update --init type1/edk2    # or just one
```

You need the bootloader sources only to re-mine commit histories or to run an
analysis tool against source.

## Using it

**To run an analysis tool**, use `scripts/analysis/run-tool.sh`. It works
through docker, so the host needs no toolchain:

```bash
./scripts/analysis/run-tool.sh --list            # what runs, what is blocked, why
./scripts/analysis/run-tool.sh codeql kexec-tools
./scripts/analysis/run-tool.sh angr /boot/efi/EFI/ubuntu/shimx64.efi
```

Of the 24 tools, 18 have runners verified against real targets. Seven of those
needed a patch, a template or a specific container environment to run at all --
[`scripts/analysis/PATCHES.md`](scripts/analysis/PATCHES.md) documents each, and
[`tools/OVERVIEW.md`](tools/OVERVIEW.md) is the table of what works on which
bootloader. The rest need a host database, specific silicon, or a commercial
licence. That spread is the SoK's finding made concrete.

**To evaluate a bug-finding tool**, pick a fix commit from
`bootloader_vuln_commits` and check out its `parent`. That parent is the last
revision that still contains the bug, so it is the version to point a tool at;
the fix commit itself is the ground truth for what the tool should find. Not
every record is a usable target — many describe code paths since removed — so
expect to select rather than run the whole set. The paper does the same, using
seven bootloaders and one commit each.

**To study a vulnerability class**, start from `bootloader_cve_db`. The
`type<N>-results.json` index carries the description, vendor and CWE-ish
`vuln_type` for each CVE, and `stats.md` breaks each type down by class and
year. The keyword breakdown tells you *why* each CVE was classified as it was.

**To scope by attack surface or bootloader type**, use the type directories.
Type 1 is where the SMM and UEFI firmware bugs are, Type 2 has the Secure Boot
bypasses, Type 3 the embedded and MCU work.

**Before trusting a number**, run `validate_dataset.py`. It currently passes
every check. It exists because the dataset previously did not: withdrawn CVEs
were still counted, two CVEs were counted under two types, statistics rows did
not sum to their own totals, and `previous_commit` pointed at the next *newer*
commit rather than the parent. Each is measured in
[`tools/docs/improvements.md`](tools/docs/improvements.md).

**To go from a CVE to a vulnerable tree**, use
`bootloader_vuln_commits/cve-commit-links.json`. It resolves 78 CVEs to their
fixing commit and to that commit's parent — the revision to check out to
reproduce the bug. [`LINKS.md`](https://github.com/BreakingBoot/bootloader_vuln_commits/blob/main/LINKS.md)
explains the coverage and why most CVEs have no linked fix.

## Refreshing the data

There is no CI. Each repository has an update script that stages a refresh
outside the submodule, prints a diff, and asks before writing:

```bash
./scripts/update-bootloader-cve-db.sh          # clones cvelistV5 if needed
./scripts/update-bootloader-vuln-commits.sh    # needs the full corpus checked out
./scripts/update-oss-bootloaders.sh
./scripts/update-papers.sh
```

Read the `RELABELLED` section before answering yes — those are CVEs that changed
bootloader type. Nothing is committed or pushed; each script prints the git
commands to publish what it changed. See [`scripts/`](scripts/).

## Citing

```bibtex
@inproceedings{glosner2026bootloader,
  title     = {SoK: All You Ever Wanted to Know About Bootloader Security
               but Were Afraid to Ask},
  author    = {Glosner, Connor and Machiry, Aravind},
  booktitle = {2026 IEEE Symposium on Security and Privacy (S\&P)},
  year      = {2026},
  doi       = {10.1109/SP63933.2026.00163}
}
```
