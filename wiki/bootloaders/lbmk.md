# lbmk

*Libreboot's build system, packaging coreboot with free payloads.*

| | |
|---|---|
| Type | **Firmware bootloader** (type1) |
| Upstream | https://codeberg.org/libreboot/lbmk |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 9 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Produces coreboot images with GRUB or SeaBIOS payloads for supported machines.

## Why it is Type 1

Type 1: a distribution of Type 1 firmware; the payload it bundles is Type 2.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **(build system)** -- lbmk assembles the boot firmware; at runtime the flow is coreboot's -- bootblock, romstage, ramstage -- followed by the payload lbmk configured.

### Passing data between stages

Libreboot's contribution is at build time rather than boot time: it fetches coreboot, patches it, supplies the board configuration, and packages a payload -- SeaBIOS, GRUB, U-Boot or a chain of them. Runtime communication is whatever that combination uses; with the common SeaBIOS-plus-GRUB arrangement, coreboot's table reaches SeaBIOS, and SeaBIOS then exposes the legacy interrupt interface that GRUB uses.

### Handoff

The handoff is coreboot's payload jump, and then the payload's own. The property Libreboot adds is what is *absent* from the image -- no Intel ME, no proprietary blobs on supported boards -- which is a supply-chain property of the artefact rather than a step in the boot flow.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type1/lbmk
./scripts/analysis/run-tool.sh codeql lbmk
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Firmware bootloader](Bootloader-Types) · [Tools](Tools)
