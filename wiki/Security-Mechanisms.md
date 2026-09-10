# Security mechanisms

What the corpus defends itself with, scanned from build configuration and source.

| Mechanism | Bootloaders |
|---|---:|
| secure boot | 30 of 62 |
| rollback protection | 28 of 62 |
| measured boot | 22 of 62 |
| signature verification | 19 of 62 |
| stack protector | 18 of 62 |
| encryption | 15 of 62 |
| fortify | 13 of 62 |
| cfi | 10 of 62 |
| aslr | 4 of 62 |

## Reading this honestly

A detection means a pattern matched build configuration or source. That is evidence the project *has* the feature — not that a given build enables it, and not that the implementation is correct. Every detection stores the file and the matched text so a claim can be checked.

Two patterns were deliberately narrowed after inspecting what they matched. `CFI` is not matched bare: in bootloaders it overwhelmingly means *Common Flash Interface*, and bare matching credited u-boot's MIPS Kconfig and wolfBoot's NXP flash HAL with control-flow integrity. `TPM` is anchored to symbol forms rather than the bare acronym.

## Declared versus enabled

Declared features are a property of the project. Binary mitigations — NX, RELRO, PIE, stack protector, FORTIFY — are a property of one build, read from an artifact with `readelf` and `nm`. A bootloader can implement Secure Boot and still compile without a stack protector, so the two are never merged.
