# Running the analysis tools

[`run-tool.sh`](run-tool.sh) runs one of the tools in
[`analysis-tools/`](../../analysis-tools/) against a bootloader.

```bash
./scripts/analysis/run-tool.sh --list                  # what can run, and what can't
./scripts/analysis/run-tool.sh codeql kexec-tools
./scripts/analysis/run-tool.sh angr /boot/efi/EFI/ubuntu/shimx64.efi
```

Results go to `analysis-results/<tool>/<target>/`. Every runner works through
docker, so the host needs no toolchain — this machine has no pip, go, cargo,
cmake or CodeQL, and the runners still work.

## What actually runs

`--list` is generated from [`tools/analysis_runners.json`](../../tools/analysis_runners.json),
which records, for all 24 tools, what each consumes and what blocks it.

| Status | Meaning | Count |
|---|---|---|
| `runnable` | Has a runner, verified against a real target | 10 |
| `needs-license` | Requires commercial software (Simics, IDA Pro) | 2 |
| `needs-hardware` | Requires the live platform or specific silicon | 3 |
| `manual` | Setup is bespoke; the project ships its own | 9 |

That spread *is* the SoK's finding in practice: most bootloader tooling is tied
to one implementation, one image format, or one piece of hardware. A runner is
not written where writing one would mean pretending a tool is more portable
than it is — in those cases the manifest says what to do instead.

## Verified runs

Every tool below was run against a real target and produced real output. The
UEFI targets are built from the corpus itself: `edk2` -> OVMF -> UEFIExtract ->
individual DXE modules.

| Tool | Target | Result |
|---|---|---|
| `codeql` | kexec-tools (source) | 78 results, 7 cpp/unbounded-write, 3 cpp/path-injection |
| `angr` | shimx64.efi | 3,017 functions; OVMF MnpDxe -> CFG recovered |
| `binwalk` | OVMF.fd | LZMA DXE volume + SecMain PE located |
| `uefi-firmware-parser` | OVMF.fd | firmware volumes, SecMain, PE32 sections |
| `fiano` | OVMF.fd | full FV/file/section tree |
| `fwhunt-scan` | OVMF MnpDxe | 94 boot services, 32 protocols, 11 GUIDs |
| `UEFITool` | OVMF.fd | 578 entries; --extract yielded 1,471 files |
| `MEAnalyzer` | OVMF.fd | correctly reports no Intel ME region present |
| `chipsec` | OVMF.fd | EFI volumes parsed offline (chipsec_util -n uefi decode) |
| `pesign` | shimx64.efi | signed by Microsoft Corporation UEFI CA 2011 |

`shimx64.efi` and `fbx64.efi` are the host's own signed bootloaders;
`kexec-tools` and `OVMF.fd` are built from the corpus.

`fwhunt-scan` drives rizin, and rizin is slow on large modules: a 25 KB DXE
driver finishes in about a minute, while 966 KB (`shimx64.efi`, which bundles
OpenSSL) had not finished in twelve. Start small.

### Building OVMF

The image the UEFI tools were verified against comes from the corpus:

```bash
git -C oss-bootloaders submodule update --init --recursive type1/edk2
# then, in the bootbench/codeql image:
make -C BaseTools && . edksetup.sh
build -a X64 -t GCC5 -p OvmfPkg/OvmfPkgX64.dsc -b RELEASE
```

Two things bite: edk2's BaseTools invokes bare `python`, which Debian does not
ship, and the build needs `nasm` and `iasl`. Both are handled in the
`bootbench/codeql` image.

## CodeQL

The one the corpus makes hardest, and the one worth explaining.

```bash
./scripts/analysis/run-tool.sh codeql <bootloader> [--build "CMD"] [--queries SUITE]
```

A C/C++ CodeQL database is built by *watching a real compile*, so the bootloader
has to build. That is the actual obstacle: most bootloaders need a cross
toolchain. [`tools/build_commands.json`](../../tools/build_commands.json) holds a
recipe per bootloader — `u-boot` and `barebox` use their sandbox targets to
avoid cross-compiling, `coreboot` builds its own toolchain and takes tens of
minutes, `opensbi` and `trusted-firmware-m` need toolchains the default image
does not carry.

Add a recipe there, or pass `--build`:

```bash
./scripts/analysis/run-tool.sh codeql u-boot --build "make sandbox_defconfig && make -j8"
```

`--queries` takes a bare suite name (`security-and-quality`, `security-extended`,
`code-scanning`) or a fully qualified pack path. Output is SARIF plus CSV.

## A docker gotcha worth knowing

If the docker daemon cannot see the output directory — a remote or rootless
daemon, or a private tmpfs — a container writes into its own empty mount and
exits 0, and you get no results and no error. The runners probe the mount first
and fail loudly instead. This is not hypothetical: it happens on this machine
for paths under `/tmp`, which is why results default to `analysis-results/`
inside the repository.

## Two more container gotchas

**Root-owned output.** Containers run as root, so anything written into a bind
mount comes back owned by root and you cannot delete your own results. Each
runner hands ownership back with `reclaim_output` when it finishes.

**Long-running images.** `fwhunt-scan` and `codeql` can run for a long time on
large inputs. If you interrupt the shell the container keeps going; find it with
`docker ps` and stop it by name. The runners never touch containers they did not
start.

## Adding a runner

Drop an executable `runners/<tool>.sh` that sources `../lib.sh`, and set
`status` and `runner` for it in `tools/analysis_runners.json`. `lib.sh` provides
`resolve_target` (bootloader name to source path), `build_command_for`,
`build_image_if_needed`, `check_mount`, and `need_docker`.
