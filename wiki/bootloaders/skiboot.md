# skiboot

*OPAL firmware for OpenPOWER.*

| | |
|---|---|
| Type | **OS bootloader** (type2) |
| Upstream | https://github.com/open-power/skiboot |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 58 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Loaded by hostboot, provides OPAL runtime services and boots a Linux kernel via petitboot.

## Why it is Type 2

Type 2: it starts from hostboot's initialised state and prepares an OS.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **entry from Hostboot** -- Hostboot loads skiboot into memory and enters it with a pointer to the HDAT hardware description.
2. **HDAT parse** -- Converts HDAT into a flattened device tree describing processors, memory, PCIe and service interfaces.
3. **hardware init** -- Initialises PCIe, the interrupt controller, NVRAM and the console.
4. **OPAL publication** -- Registers the OPAL runtime call interface the OS will use.
5. **payload boot** -- Loads the payload from PNOR -- normally a Linux kernel running Petitboot -- and enters it.

### Passing data between stages

skiboot's input is HDAT and its output is a device tree, and that translation is most of what it does: everything the OS learns about the machine arrives as device tree nodes and properties. After the handoff, communication is OPAL calls -- an `OPAL_CALL` into firmware for console, PCI, NVRAM, sensors and error logging -- plus an asynchronous message queue the OS polls. skiboot stays resident in hypervisor-privileged memory for the life of the system.

### Handoff

The kernel is entered with `r3` pointing at the flattened device tree, in which the `/ibm,opal` node tells the OS the firmware's entry point and base. That kernel is usually not the final OS but a small Linux running Petitboot, which then kexecs into the real one.

## Security mechanisms

Detected in its build configuration and source:

- cfi
- encryption
- measured boot
- rollback protection
- secure boot
- signature verification
- stack protector

See [Security-Mechanisms](Security-Mechanisms) for how these are detected and what a detection does and does not prove.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type2/skiboot
./scripts/analysis/run-tool.sh codeql skiboot
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [OS bootloader](Bootloader-Types) · [Tools](Tools)
