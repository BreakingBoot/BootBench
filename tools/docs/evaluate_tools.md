# `evaluate_tools.py`

Scores an analysis tool against BootBench's CVE-linked ground truth.

```bash
python3 evaluate_tools.py --list
python3 evaluate_tools.py --tool codeql --bootloader u-boot --limit 3
python3 evaluate_tools.py --tool codeql --bootloader shim --queries code-scanning
```

## How it works

`cve-commit-links.json` resolves CVEs to a fixing commit and to that commit's
parent — a revision that still contains the bug. For each target the harness
checks the parent out into a git worktree, runs the tool, and compares its
findings against the files the fix went on to change.

## What a "hit" is, and is not

A finding counts as a **`file_hit`** when it lands in a file the fix touched.
That is a proxy, not proof: the tool may have flagged the right file for the
wrong reason, and a fix spanning many files is easier to hit. It is reported as
`file_hit` rather than "true positive" for exactly that reason.

Findings elsewhere are counted but **not** called false positives. A bootloader
has other bugs; this ground truth knows about one.

Anyone building the paper's evaluation table should treat `file_hit` as a
screening signal and confirm the surviving findings by hand.

## Targets

148 CVE-linked targets: u-boot 39, mu_basecore 29, grub 27, edk2 25, shim 24,
arm-trusted-firmware 2, edk2-platforms 2.

Only source-level tools can use these, and only where the bootloader builds —
`u-boot` is the one target bootloader with a verified build recipe today. The
others need recipes adding to `build_commands.json` before they can be scored.
