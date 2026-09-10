# `scan_defenses.py`

Inventories what each bootloader *defends itself with*. BootBench otherwise
records only where bootloaders went wrong.

```bash
python3 scan_defenses.py --root .. \
    --output ../oss-bootloaders/defenses.json \
    --markdown ../oss-bootloaders/DEFENSES.md \
    --binary path/to/built.efi
```

About 8 minutes for the full 63-bootloader corpus.

## Two sources, deliberately kept apart

**Declared features**, from build configuration and source. Whether a project
*supports* Secure Boot, measured boot, signature verification, rollback
protection or encryption is a property of the project.

**Binary mitigations**, from a built artifact via `readelf` and `nm` — no other
tooling. Whether NX, RELRO, BIND_NOW, PIE, stack protector or FORTIFY are
actually *on* is a property of one build, not of the project.

A bootloader can implement Secure Boot and still compile without a stack
protector. Collapsing the two would state something false about both.

## Current picture

| Mechanism | Bootloaders |
|---|---:|
| Secure Boot / verified boot | 30 of 63 |
| Rollback / anti-downgrade | 28 of 63 |
| Measured boot / TPM | 22 of 63 |
| Image signature verification | 19 of 63 |
| Stack protector (declared) | 18 of 63 |
| Image encryption | 15 of 63 |
| FORTIFY_SOURCE (declared) | 13 of 63 |
| Control-flow integrity | 10 of 63 |
| Load-address randomisation | 4 of 63 |

Fewer than half the corpus implements Secure Boot, and four bootloaders
randomise their load address.

## Reading it honestly

A tick means a pattern matched build configuration or source, which is evidence
the project has the feature — not that any particular build enables it, and not
that the implementation is correct. Each detection stores the file and matched
text in `defenses.json` so a claim can be checked rather than trusted.

Two patterns were deliberately narrowed after checking their evidence:

* **`CFI` is not matched bare.** In bootloaders it overwhelmingly means *Common
  Flash Interface*, the NOR flash standard. Bare matching flagged u-boot's MIPS
  Kconfig and wolfBoot's NXP flash HAL as having control-flow integrity. It now
  needs `fsanitize=cfi`, `CFI_CLANG`, `SHADOW_CALL_STACK` or similar.
* **`TPM` is anchored to symbol forms** (`CONFIG_TPM`, `TPM2_`, `tpm2_extend`)
  rather than the bare acronym.

That is the same failure mode as the `dos` vulnerability keyword: a short
acronym that means something else in this domain. Widen a pattern only after
looking at what it actually matched.
