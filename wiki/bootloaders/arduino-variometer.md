# arduino-variometer

*Arduino variometer project including its bootloader.*

| | |
|---|---|
| Type | **Monolithic bootloader** (type3) |
| Upstream | https://github.com/prunkdump/arduino-variometer |
| CVEs attributed | 0 |
| Vulnerability-fixing commits | 0 naming a CVE, 0 keyword-matched |
| CVEs with a linked fix | 0 |

## What it does at boot

Application firmware with a small bootloader for a flight instrument.

## Why it is Type 3

Type 3: reset to application on AVR.

## How it boots

See [Boot-Stages](Boot-Stages) for the eight-stage model these phases map onto.

```mermaid
%%{init: {"flowchart": {"htmlLabels": true, "curve": "linear"}}}%%
flowchart TD
    ENTRY(["Hardware<br/>power-on / reset"]):::edge
    S0["<b>bootloader</b>"]:::stage
    S1["<b>application start</b>"]:::stage
    S2["<b>calibration data load</b>"]:::stage
    S3["<b>main loop</b>"]:::stage
    TARGET(["Flight instrument<br/>(running)"]):::edge
    ENTRY --> S0
    S0 -->|"rjmp 0 to the sketch"| S1
    S1 -->|"sensors initialised"| S2
    S2 -->|"calibration values from EEPROM"| S3
    S3 -->|"sensor fusion, display and audio"| TARGET
    classDef stage fill:#eef3fb,stroke:#4a6fa5,stroke-width:1px;
    classDef edge fill:#f6f6f6,stroke:#888,stroke-dasharray:3 3;
```

1. **bootloader** -- A stock AVR bootloader (Optiboot or similar) occupies the boot section and provides serial programming.
2. **application start** -- The variometer firmware starts and initialises its sensors -- barometer, accelerometer, magnetometer, GPS.
3. **calibration data load** -- Calibration values are read from EEPROM, where the separate calibration sketches in this repository wrote them.
4. **main loop** -- Runs the flight instrument: sensor fusion, display and audio output, logging.

### Passing data between stages

This project is application firmware with a conventional AVR bootloader beneath it, and the only state crossing that boundary is EEPROM: calibration written by one sketch is read by another. It is included in the corpus as a worked example of the Type 3 pattern at its simplest -- reset goes to a small serial-programmable loader, which goes to an application that owns the device -- rather than for the bootloader being novel.

### Handoff

The jump to the application is the AVR bootloader's `rjmp` to address 0, with nothing passed. There is no verification anywhere in the path.

## Security mechanisms

None detected. That means no matching pattern was found in its build configuration or source, not that the project is insecure -- a small MCU bootloader may simply have nothing to configure.

## Analysing it

```bash
git -C oss-bootloaders submodule update --init type3/arduino-variometer
./scripts/analysis/run-tool.sh codeql arduino-variometer
```

See [Tools](Tools) for what each tool applies to.

---

[Home](Home) · [Monolithic bootloader](Bootloader-Types) · [Tools](Tools)
