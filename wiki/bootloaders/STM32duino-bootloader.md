# STM32duino-bootloader

*USB DFU bootloader for STM32F1 boards.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/rogerclarkmelbourne/STM32duino-bootloader |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Enumerates as a DFU device for upload, then jumps to the sketch.

## Why it is Type 3

Type 3: reset to application.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

1. **reset into bootloader** -- Occupies the first 8 or 16 KB of STM32F1 flash.
2. **button/flag check** -- Checks the BOOT jumper, a button, or a magic value left in a backup register by the application.
3. **USB DFU enumeration** -- Enumerates as a USB DFU device using the bundled ST USB library.
4. **download** -- Receives the application image over DFU and writes it to the application offset.
5. **application jump** -- Relocates the vector table to the application offset and jumps.

### Passing data between stages

The bootloader and the Arduino core agree on a flash offset (0x8002000 or 0x8005000) and on the backup-register magic value that means "reset into DFU" -- that pair is the entire interface. Because the vector table has to be moved, the application must set VTOR to the same offset, which is why an image built for the wrong offset simply hangs.

### Handoff

Nothing is passed to the application. There is no verification of what was downloaded; the USB DFU path is open whenever the device is in bootloader mode, which is the characteristic exposure of this class of hobbyist bootloader.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/STM32duino-bootloader
./scripts/analysis/run-tool.sh codeql STM32duino-bootloader
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
