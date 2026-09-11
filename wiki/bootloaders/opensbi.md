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

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **_start** -- The first hart enters the firmware; others are held in a wait loop. Sets up the stack and the per-hart scratch space.
2. **cold boot path** -- The boot hart relocates the firmware if needed, initialises the console and platform, and parses the device tree.
3. **warm boot path** -- Each remaining hart initialises its own trap handling, timers and interrupt controller.
4. **sbi_init** -- Registers ecall extensions (timer, IPI, HSM, reset) and defines the domains that partition memory and devices.
5. **next stage** -- Configures PMP for the next stage's domain and drops from M-mode to S-mode at the payload's entry point.

### Passing data between stages

OpenSBI passes forward a device tree, which it may edit first -- reserving its own memory so the next stage does not use it, and adding nodes for what it manages. After the transition the interface is not a table but the `ecall` instruction: the S-mode payload traps into M-mode for timers, IPIs, hart state management and system reset. The three build shapes differ only in where the next stage comes from: FW_JUMP jumps to a fixed address, FW_PAYLOAD embeds the next stage in the firmware image, and FW_DYNAMIC takes its parameters from a struct the previous loader filled in.

### Handoff

The handoff is an `mret` into S-mode with `a0` set to the hart ID and `a1` to the physical address of the device tree -- the same convention the Linux RISC-V kernel expects. PMP entries are programmed first so the supervisor cannot reach firmware memory. OpenSBI stays resident in M-mode for the life of the system.

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
