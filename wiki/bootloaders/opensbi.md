# opensbi

*RISC-V Supervisor Binary Interface reference implementation.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/riscv-software-src/opensbi |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 28 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Runs in M-mode, sets up the machine, provides the SBI ABI, then enters S-mode at the next stage.

## Why it is Type 1

Type 1: it is the privileged firmware layer presenting a stable interface to whatever boots next -- the RISC-V analogue of UEFI's role.

## Security mechanisms

Detected in its build configuration and source:

- rollback protection
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/opensbi
./scripts/analysis/run-tool.sh codeql opensbi
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
