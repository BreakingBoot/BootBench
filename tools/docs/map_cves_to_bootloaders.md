# `map_cves_to_bootloaders.py`

Resolves each CVE to the corpus bootloaders it affects, so a researcher can
select the CVEs for the bootloader they are studying.

```bash
python3 map_cves_to_bootloaders.py --root ..          # dry run
python3 map_cves_to_bootloaders.py --root .. --write  # store the field
```

## Why it is needed

The classifier answers "is this CVE about *a* bootloader" and stops. Without
this, `containerd`, `OpenStack Ironic` and `Xen` sit in the database
indistinguishable from genuine entries like `barebox`.

## Three signals, ranked

| `matched_on` | Meaning | Trust |
|---|---|---|
| `affected` | the record's vendor/product list names the project | highest |
| `reference` | a reference URL points at the project's repository | medium |
| `description` | the description names the project | lowest |

Each hit records which signal produced it, so a consumer can filter on
confidence instead of trusting one opaque label.

## Coverage

289 of 1,432 CVEs (20%) resolve to a corpus bootloader — `grub` 93, `u-boot`
70, `shim` 35, `edk2` 34. The other 80% are mostly OEM firmware advisories
(CPG BIOS, HP PC BIOS, AMD processors) which are Type 1 firmware but not corpus
projects, and they resolve to an empty list rather than a guess.

## The trap this avoids

Two corpus directories are named after ordinary words: `type3/firmware`
(Meshtastic) and `type2/bootloader` (rust-osdev). Matching those bare hit 388
and 207 CVEs respectively, none of which says anything about those projects.
Generic names and names under four characters resolve only through an explicit
alias — the same discipline the `dos` keyword needed.

Verified against known CVEs: BootHole (CVE-2020-10713) resolves to `grub`,
CVE-2023-40547 and CVE-2022-28737 to `shim`, CVE-2019-13104 to `u-boot`.
