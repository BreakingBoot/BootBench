# `verify_claims.py`

Checks the wiki's technical claims against the source they describe.

```bash
python3 tools/verify_claims.py            # re-check the recorded evidence
python3 tools/verify_claims.py --write    # refresh it after editing prose
```

## Why it exists

Everything else in [`wiki/`](../../wiki/) is generated from the datasets, so it
cannot say anything the data does not. The prose in
[`wiki_content.py`](../wiki_content.py) is the exception: it is written, so it
is the one part that can be wrong.

Most of that prose names something concrete — a stage, a symbol, a structure, a
GUID, a file. Those names either appear in the project's own tree or they do
not. This walks every backticked identifier and every stage name, greps the
bootloader's own submodule, and records the file where each was found in
[`claim_evidence.json`](../claim_evidence.json).

## Reading the output

```
[INFO] 151 of 158 claimed identifiers located in source; 10 explained as cross-references
[OK] every claimed identifier is either found in source or explained
```

An identifier that is not found must have an entry under `cross_reference`
giving the reason. There are three legitimate reasons, and nothing else
qualifies:

| Reason | Example |
|---|---|
| The name belongs to another project | `BlParseLib` is edk2 code, named on coreboot's page because it consumes coreboot's table |
| The claim is one of absence | Chameleon's page says there is *no* `boot.efi` in its chain |
| The tree is not checked out here | `firmware-open` vendors coreboot and edk2 as nested submodules |

An unexplained miss fails the run. `test_every_claimed_identifier_has_evidence`
is the fast half: it checks the record covers what the prose currently says,
without re-running the greps, so editing prose without re-recording fails the
suite.

## What it does not cover

A name being present in the source proves the name is real. It does not prove
the sentence around it is right — that `spl_image_info` exists does not prove
SPL passes it to U-Boot. Claims about *behaviour* were checked by reading the
code and, where the SoK covers the bootloader, against the paper; the
`case_study` field records which sections those are.

Claims taken from the paper rather than from source are cited in the prose by
section number, and `test_case_study_citations_are_paper_sections` pins which
bootloaders may carry one.
