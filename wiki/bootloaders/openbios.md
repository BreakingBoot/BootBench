# openbios

*Free IEEE 1275 Open Firmware implementation.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://github.com/openbios/openbios |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 16 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Provides a Forth interpreter and device tree, then boots a client program.

## Why it is Type 1

Type 1: it is the firmware interface itself, exposing device abstractions rather than preparing a specific OS.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **entry and kernel bring-up** -- Architecture-specific entry code sets up a stack and starts the Forth virtual machine.
2. **dictionary load** -- The compiled Forth dictionary is unpacked, giving the interpreter its vocabulary.
3. **device probing** -- Drivers probe buses and instantiate packages, building the IEEE 1275 device tree under /packages.
4. **client interface** -- The Open Firmware client interface is published and a boot device is selected, then the client program is loaded and entered.

### Passing data between stages

Everything is the device tree. Each node carries properties -- `reg`, `compatible`, `device_type` -- and methods callable through the interface, so a later stage discovers hardware by walking the tree rather than by being handed a table. Persistent configuration lives in NVRAM: `boot-device`, `boot-args`, and `nvramrc`, a Forth script run at start-up that can patch the tree before anything else sees it. The Forth dictionary itself is state, so a client can define and call new words at runtime.

### Handoff

OpenBIOS loads the client program and enters it with a pointer to the client interface handler in a well-known register. The client keeps calling back into firmware -- `finddevice`, `getprop`, `claim`, `read` -- to walk the tree and allocate memory, which is why the firmware stays resident rather than being torn down. The OS takes ownership when it stops making those calls.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/openbios
./scripts/analysis/run-tool.sh codeql openbios
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
