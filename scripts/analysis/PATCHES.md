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

## efi_fuzz — patched

Last touched March 2021 and pins nothing, so five things have drifted.
[`patches/efi_fuzz-modernise.patch`](patches/efi_fuzz-modernise.patch) fixes
all of them:

1. `bootstrap.pypa.io/get-pip.py` now needs Python 3.10+, but the Dockerfile is
   Ubuntu 20.04 (Python 3.8). pypa keeps per-version scripts; use the 3.8 one.
2. uefi-firmware-parser's main branch moved to `requires-python >=3.10`. 1.11
   is the last release that installs on 3.8.
3. `requirements.txt` asks for an unpinned `qiling`, now resolving to 1.4.x.
   Pinned to 1.2.4, contemporary with efi_fuzz.
4. Qiling renamed the constructor's `output` string to `verbose`, taking a
   `QL_VERBOSE` enum, before 1.2.4:
   `TypeError: __init__() got an unexpected keyword argument 'output'`.
5. qiling 1.2.4 indexes x86 control registers newer unicorn no longer exports:
   `NameError: name 'UC_X86_REG_CR5' is not defined`. Pinned to unicorn 1.0.3.

**A trap worth naming.** The Dockerfile copies only `requirements.txt`; the
source is mounted at run time. Patching just the build context therefore leaves
the Qiling fix out of the code that actually executes. The runner keeps one
patched checkout and uses it for both the build and the mount.

## emba — no patch, but four prerequisites

emba works, and produces a full HTML report, once all four are met:

1. **Populate `external/`.** The image ships an empty `/emba` and expects the
   source mounted. A bare checkout fails every dependency check. Run the
   installer once against the checkout (about 4 GB):

   ```bash
   docker build -t bootbench/emba-installer - <<'EOF'
   FROM embeddedanalyzer/emba:2.0.3c
   RUN apt-get update && apt-get install -y --no-install-recommends docker.io
   EOF
   docker run --rm --privileged --pid=host \
       -v "$PWD/analysis-tools/dynamic/emba:/emba" \
       -v /var/run/docker.sock:/var/run/docker.sock \
       bootbench/emba-installer -c 'yes | ./installer.sh -g -f'
   ```

2. **A docker client inside the installer image.** The installer's
   `I05_emba_docker_image_dl` module refuses to continue without docker, and
   the emba image has no client.

3. **`--pid=host`.** That module checks for the daemon with `pgrep dockerd` —
   a process check, not a socket check — so mounting the socket is not enough.

4. **`config/gh_action` and the `-i` flag.** Without `gh_action` emba demands a
   populated CVE-search SQLite database; its own CI uses that marker to skip
   the check. Without `-i` emba believes it is on a host and tries to
   `modprobe ufs nandsim ubi nbd`, which fails and aborts.

## karonte — no patch, but the firmware comes from elsewhere

Like BootStomp, karonte is pinned to an angr generation that no longer
installs, and the authors publish `badnack/karonte` with a working virtualenv
at `/home/karonte/.virtualenvs/karonte`, off the default PATH.

Two further wrinkles:

* Its `config/lk/*.json` reference `./firmware/lk/lk_latest` and
  `lk_unpatched`, which it does not ship. **BootStomp does**, under
  `bootloaders/qualcomm_lk/`, with exactly those names — same research group.
  The runner stages them across.
* The image's karonte tree is not writable by the `karonte` user, and a
  recursive copy fails on router firmware samples that are not world-readable,
  leaving `tool/` missing. The runner rewrites the config's `bin` to an
  absolute path under the output mount instead of copying the tree.

Karonte is slow: a multi-binary taint analysis of the 3.6 MB LK image runs for
hours, which matches the timings in its paper.

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
| `tsffs` | Requires Intel Simics, which is not freely redistributable. |
| `emmutaler` | Needs decrypted Apple iBoot images, which are not distributable. |
| `ASPFuzz` | Targets the AMD Secure Processor ROM on specific silicon. |
| `firmadyne` | Same architecture as FirmAE and superseded by it: needs a host PostgreSQL database plus prebuilt QEMU kernels. Emulates Linux router firmware, not bootloaders. |
| `FirmAE` | Its download.sh and docker-init.sh do run unattended (the fcore image builds), but init.sh then does `sudo service postgresql restart` against a PostgreSQL instance on the host, which the fcore image does not contain. It also emulates Linux router firmware, so BootBench holds no target for it. |
| `FACT_core` | Multi-container deployment with its own database, worker pool and web UI, installed by its own scripts against the host. Analyses whole firmware images rather than bootloaders specifically. |
| `karonte` | No packaging of any kind, and pinned to an angr generation that no longer installs. Needs the same treatment as BootStomp: a period-correct container image, which the authors did not publish. |
