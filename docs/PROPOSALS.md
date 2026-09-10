# Improving BootBench for bootloader security research

What the dataset cannot currently answer, why, and what to change. Every number
below was measured against the data as it stands; the commands are in
[`tools/`](../tools/).

## The gap in one sentence

BootBench records **where bootloaders went wrong** and says nothing about
**what defends them** — so it supports the SoK's vulnerability sections and
leaves its hardening section without data.

Beyond that, the vulnerability half is stored as free text where structured
fields were available in the source records and thrown away.

---

## What the data cannot answer today

| Question a researcher would ask | Answerable? | Why not |
|---|---|---|
| Which CWE classes dominate bootloader bugs? | No | `vuln_type` is 320 distinct free-text strings for 1,432 CVEs; 444 (31%) are `n/a`, `other` or `tbd`. |
| Which of these CVEs are high severity? | No | No CVSS stored, though 1,006 records (70%) carry one. |
| Show me every GRUB CVE. | No | Nothing records which bootloader a CVE affects. 594 CVEs (41%) have no usable affected-product data at all. |
| Which bootloaders support Secure Boot / measured boot / rollback protection? | No | No defense data of any kind. |
| Which compile with stack protector, RELRO, NX, PIE? | No | Same. |
| Which attack surfaces does bootloader X expose? | No | The SoK's six surfaces exist only as prose in the paper. |
| How large / what architecture / what language is each bootloader? | No | `table.md` has commits and dates only. |
| Which tool finds which class of bug, on which bootloader? | Partly | 18 tools run, but no finding is tied to ground truth. |

---

## Proposals, in priority order

### P1 — Extract the structured fields already in the CVE records

**Cost: low. Value: high. No new data collection.**

The CVE 5.x records the dataset already stores contain fields the pipeline
discards:

| Field | Present in | Currently stored |
|---|---|---|
| `cweId` (structured) | 934 CVEs (65%) | no |
| CWE recoverable at all | 957 CVEs (67%) | no |
| CVSS metrics | 1,006 CVEs (70%) | no |
| affected vendor/product list | 838 CVEs (59%) | first vendor only |

Adding `cwe_ids`, `cvss`, and the full `affected` list to
`type<N>-results.json` replaces 320 free-text strings with 181 real CWEs and
makes severity, attack vector and vulnerability-class analysis possible in one
pass. This is the single highest value-per-effort change available.

*Change:* extend `parse_cve()` in `tools/classify_cves.py`; regenerate.

### P2 — Record which bootloader each CVE affects

**Cost: medium. Value: high.**

The classifier answers "is this CVE about *a* bootloader" and stops there.
Nothing maps a CVE to a corpus entry, so a researcher cannot select the CVEs
for the bootloader they are studying.

The consequence shows up as noise: `containerd`, `OpenStack Ironic`, `Xen` and
`radare2` are all currently in the bootloader CVE database, while genuine
entries like `barebox` sit beside them with no way to tell them apart.

*Change:* add a `bootloaders: []` field resolved from the affected-product list
and the description against the corpus, plus `confidence`. Where nothing
resolves, say so — an explicit `unresolved` is more useful than an implied
match.

### P3 — Publish a defense inventory

**Cost: medium. Value: high — this is the missing half of the dataset.**

Nothing in BootBench records what protects a bootloader. Two complementary
sources, both demonstrated to work on this corpus:

**Binary mitigations**, from a built artifact with `readelf` and `nm` alone —
no extra tooling. Verified on the corpus build of `kexec`:

| NX | RELRO | BIND_NOW | PIE | stack protector | FORTIFY |
|---|---|---|---|---|---|
| yes | yes | yes | yes | yes | yes |

**Declared security features**, from source. `u-boot`, `barebox` and `coreboot`
all carry Kconfig options for stack protection; the same scan can find
signature verification, measured boot, rollback protection and Secure Boot
support.

*Change:* a `tools/scan_defenses.py` producing `defenses.json` per bootloader,
and a table in the corpus README. This turns "what is the state of the art of
bootloader security mechanisms" from an essay question into a query, and gives
the SoK's hardening section the evidence it currently lacks.

### P4 — Encode the attack-surface taxonomy

**Cost: low. Value: high for navigation.**

The paper defines six surfaces — invasive hardware, external hardware, remote
access, persistent data sources, post-boot features, boot-time features — and
maps bootloader types onto them. None of that is in the data.

*Change:* an `attack_surfaces` field per bootloader in a corpus manifest, and
per CVE where the description supports it. It makes the dataset navigable along
the axis the paper actually argues in, and lets someone ask "which tools cover
which surfaces" against real entries rather than the paper's table.

### P5 — Characterise the corpus

**Cost: low. Value: medium.**

Table 1 of the SoK — architectures, supported OSs, activity, CI — exists only
in the paper. `table.md` has commit counts and dates.

*Change:* extend `tools/generate_table.py` to record language breakdown, source
size, architectures (from build targets or Kconfig), licence, and last release.
Cheap, and it makes the corpus self-describing.

### P6 — Turn tool runs into an evaluation matrix

**Cost: high. Value: high for the paper specifically.**

18 of 24 analysis tools now run, which is a stronger result than the SoK
reports, but each has been run against a single target and no finding is
checked against ground truth.

*Change:* run each tool across the CVE-linked targets in
`cve-commit-links.json` (78 CVEs with a known-vulnerable parent revision) and
score true and false positives. That converts anecdotes into the
tool × bootloader × bug-class matrix the paper's evaluation needs.

### P7 — Widen the CVE-to-fix linkage

**Cost: high. Value: medium.**

78 of 1,432 CVEs resolve to a fixing commit. Patch URLs in the CVE records do
not help — only 31 records (2%) point at a git commit.

Better routes, in order of expected yield: distribution advisories (Red Hat,
Debian and SUSE errata name both the CVE and the patched package version);
project security advisories on GitHub; and the 120 orphan CVE references
already found in commit messages, which are a bounded, evidence-derived
candidate list rather than a guess.

---

## What not to do

**Do not widen the vulnerability keyword list.** This was measured: recovering
the 28 known-missed security commits costs roughly 100 extra records each, and
the broadest variant still misses 9 of them. See
[`tools/docs/improvements.md`](../tools/docs/improvements.md). Keyword matching
has been taken about as far as it goes; P1 and P2 add structure instead of
widening a net.

**Do not treat the CVE count as a measure of bootloader insecurity.** 41% of
entries have no affected-product data, and the classifier matches descriptions,
not components. The count is a corpus size, not a finding.

---

## Suggested order

P1 and P4 are small and unlock the rest. P3 is the one that changes what the
repository is *for*: it makes BootBench a picture of bootloader security rather
than only of bootloader failure.
