# Getting the harder tools running

Most of these projects were published alongside a paper and have not been
touched since. They break against current dependencies in predictable ways.
This is what each one needs, and where a code change was required, the patch
that makes it work.

Patches live in [`patches/`](patches/) and are applied automatically by the
runner that needs them — you do not have to apply them by hand, and the
submodules are left untouched.

## arbiter — patched

Three separate defects stop it running on a real binary.

**1. angr API drift.** `setup.py` pins `angr==9.0.10576`, but the shipped
Dockerfile installs angr unpinned, so a fresh build resolves 9.2.x, where
`archinfo` is no longer re-exported from `angr`:

```
ImportError: cannot import name 'archinfo' from 'angr'
```

**2. A dead guard.** `CheckpointHook` protects its initialisation of
`state.globals['sym_vars']` with `state.globals.get('globals')` — a key that
never exists, so the guard tells it nothing.

**3. Uninitialised taint state.** Every hook appends to
`state.globals['sym_vars']` and `['derefs']` assuming some earlier hook created
them. Which hook fires first depends on the binary, so on a real target:

```
KeyError: 'sym_vars'
```

All three are fixed by [`patches/arbiter-angr-api.patch`](patches/arbiter-angr-api.patch).

**Also needed: a usable template.** Arbiter is driven by a "vulnerability
description" naming the sinks, the sources, and the constraint that makes a
value dangerous. The templates it ships target the Juliet test suite
(`printUnsignedLine`, `badSource`) and match nothing in firmware. Two
non-obvious details:

* `run_arbiter.py` calls `template.apply_constraint`, but every shipped
  template defines `constrain`, so they fail with `AttributeError`.
* The tracked argument name is a **role label, not the real parameter name**.
  `Target.sz` is hardcoded to `args.index('n')`, so a size argument must be
  called `n` regardless of what the prototype says — angr calls it `size` for
  `memcpy` and `eltsize` for `calloc`. Using the real name gives
  `ValueError: 'n' is not in list`.

[`templates/bootloader_CWE190.py`](templates/bootloader_CWE190.py) is a working
template for integer overflow into a UEFI, U-Boot or libc allocation.

## BootStomp — no patch, but the environment matters

BootStomp is Python 2 with a pinned old angr, and cannot be installed on a
current system. The authors' prebuilt image `badnack/bootstomp` still works.

The trap: the image has BootStomp at `/home/angr/BootStomp` and angr in a
virtualenv at `/home/angr/.virtualenvs/angr`, owned by the `angr` user and
**not on the default PATH**. Mounting your own checkout and running `python`
gives `ImportError: No module named angr`. Run as `-u angr`, source the
virtualenv, and use the image's own copy.

It is also not a general tool: it needs a per-image config supplying
architecture, thumb mode and the unlock-check address. It ships those configs
and the matching Android bootloader images, including a Qualcomm LK — the same
bootloader the corpus carries as `type2/lk`.

## uefi_retool — half of it works

`get-info` and `get-pp` drive IDA Pro and cannot run without a licence.
`get-images` uses `uefi-firmware-parser` and does not, so module extraction
works: 113 modules out of OVMF.

## top4grep — needs its corpora

Fails on first run with a missing `punkt_tab` tokeniser. Add
`python -m nltk.downloader punkt punkt_tab` to the image. The shipped database
is empty; pass `--build-db` to populate it from dblp.

## fwupd — offline half only

`fwupdtool firmware-parse` and `firmware-extract` work in a container and tell
you how fwupd would interpret an image. It prompts for the container format if
not told one, so pass `--type` (`pefile` for a UEFI application, `efi-volume`
for a firmware volume); the runner guesses from `file(1)`.

Applying an update still needs the live platform.

## Still blocked, and why

| Tool | Blocker |
|---|---|
| tsffs | Intel Simics. There is a free public release, but it is behind registration and cannot be fetched unattended. |
| emmutaler | Needs decrypted Apple iBoot images, which are not distributable. |
| ASPFuzz | Targets AMD Secure Processor ROM on specific silicon. |
| chipsec (on-target) | The SMM, SPI and Secure Boot modules need a kernel driver on the live platform. The offline image decoder runs. |
| karonte | No packaging at all, and pinned to an angr generation that no longer installs. Needs the same treatment as BootStomp: a period-correct image. |
| firmadyne | Needs a populated postgres database plus prebuilt QEMU kernels. Superseded by FirmAE, which automates the same workflow. |
| FACT_core | Multi-container deployment with its own compose stack; follow the project's install rather than wrapping it. |
| efi_fuzz | Builds Triton 0.8.1 and Capstone 4.0.2 from source on Ubuntu 20.04, then needs a per-driver harness. The build is viable; the harness is per-target work. |
