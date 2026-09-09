# Bootloader papers, by contribution

146 papers matched from 7 venues, 2015 onwards. 16 name the boot chain in their title (**core**); the rest matched a broader firmware or embedded-systems term (**context**) and are the literature the SoK's tool survey draws on.

Regenerate with:

```bash
python3 tools/collect_papers.py --since 2015 \
    --output papers.json --markdown PAPERS.md
```

Contribution is assigned from the title by the ordered rules in [`tools/bootbench_keywords.py`](tools/bootbench_keywords.py) (`PAPER_CONTRIBUTIONS`), first match wins.

## Contents

- [Systematization and measurement](#systematization-and-measurement) — 6
- [Attacks and case studies](#attacks-and-case-studies) — 16
- [Vulnerability discovery](#vulnerability-discovery) — 57
- [Rehosting and emulation](#rehosting-and-emulation) — 13
- [Defenses, verification and hardening](#defenses-verification-and-hardening) — 17
- [Other boot- and firmware-related work](#other-boot--and-firmware-related-work) — 37

## Systematization and measurement

**Core** (3)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2026 | IEEE S&P | [SoK: All You Ever Wanted to Know About Bootloader Security but Were Afraid to Ask](https://doi.org/10.1109/SP63933.2026.00163) | `bootloader` |
| 2026 | USENIX Security | [SoK: 20 Years of Power, Privilege, and Peril in x86 System Management Mode](https://www.usenix.org/conference/woot26/presentation/louka) | `system management mode` |
| 2020 | USENIX Security | [Shattered Chain of Trust: Understanding Security Risks in Cross-Cloud IoT Access Delegation](https://www.usenix.org/conference/usenixsecurity20/presentation/yuan) | `chain of trust` |

**Context** (3)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2026 | IEEE S&P | [Responsible Disclosure is a Two-Way Street: Empirically Measuring the Responsible Disclosure Contract in the Firmware Ecosystem](https://doi.org/10.1109/SP63933.2026.00180) | `firmware` |
| 2024 | USENIX Security | [SOK: 3D Printer Firmware Attacks on Fused Filament Fabrication](https://www.usenix.org/conference/woot24/presentation/rais) | `firmware` |
| 2020 | IEEE S&P | [SoK: Understanding the Prevailing Security Vulnerabilities in TrustZone-assisted TEE Systems](https://doi.org/10.1109/SP40000.2020.00061) | `trustzone` |

## Attacks and case studies

**Core** (3)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2025 | USENIX Security | [BOOTKITTY: A Stealthy Bootkit-Rootkit Against Modern Operating Systems](https://www.usenix.org/conference/woot25/presentation/lee) | `bootkit` |
| 2024 | USENIX Security | [Achilles Heel in Secure Boot: Breaking RSA Authentication and Bitstream Recovery from Zynq-7000 SoC](https://www.usenix.org/conference/woot24/presentation/ravi) | `secure boot` |
| 2017 | USENIX Security | [BADFET: Defeating Modern Secure Boot Using Second-Order Pulsed Electromagnetic Fault Injection](https://www.usenix.org/conference/woot17/workshop-program/presentation/cui) | `secure boot` |

**Context** (13)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2026 | NDSS | [Through the Authentication Maze: Detecting Authentication Bypass Vulnerabilities in Firmware Binaries](https://www.ndss-symposium.org/ndss-paper/through-the-authentication-maze-detecting-authentication-bypass-vulnerabilities-in-firmware-binaries/) | `firmware` |
| 2026 | USENIX Security | [DisARMed: Attacking ARM TrustZone from Userspace with Memory Aliasing](https://www.usenix.org/conference/woot26/presentation/henes) | `trustzone` |
| 2025 | ACM CCS | [BadAML: Exploiting Legacy Firmware Interfaces to Compromise Confidential Virtual Machines](https://doi.org/10.1145/3719027.3765123) | `firmware` |
| 2025 | ASE | [FirmProj: Detecting Firmware Leakage in IoT Update Processes via Companion App Analysis](https://doi.org/10.1109/ASE63991.2025.00171) | `firmware` |
| 2025 | NDSS | [SCRUTINIZER: Towards Secure Forensics on Compromised TrustZone](https://www.ndss-symposium.org/ndss-paper/scrutinizer-towards-secure-forensics-on-compromised-trustzone/) | `trustzone` |
| 2024 | NDSS | [Faults in Our Bus: Novel Bus Fault Attack to Break ARM TrustZone](https://www.ndss-symposium.org/ndss-paper/faults-in-our-bus-novel-bus-fault-attack-to-break-arm-trustzone/) | `trustzone` |
| 2023 | USENIX Security | [Oops..! I Glitched It Again! How to Multi-Glitch the Glitching-Protections on ARM TrustZone-M](https://www.usenix.org/conference/usenixsecurity23/presentation/sass) | `trustzone` |
| 2022 | IEEE S&P | [Abusing Trust: Mobile Kernel Subversion via TrustZone Rootkits](https://doi.org/10.1109/SPW54247.2022.9833891) | `trustzone` |
| 2022 | NDSS | [FANDEMIC: Firmware Attack Construction and Deployment on Power Management Integrated Circuit and Impacts on IoT Applications](https://www.ndss-symposium.org/ndss-paper/8485/) | `firmware` |
| 2021 | IEEE S&P | [CANNON: Reliable and Stealthy Remote Shutdown Attacks via Unaltered Automotive Microcontrollers](https://doi.org/10.1109/SP40001.2021.00122) | `microcontroller` |
| 2020 | USENIX Security | [TPM-FAIL: TPM meets Timing and Lattice Attacks](https://www.usenix.org/conference/usenixsecurity20/presentation/moghimi-tpm) | `tpm` |
| 2017 | ACM CCS | [Side-Channel Attacks on BLISS Lattice-Based Signatures: Exploiting Branch Tracing against strongSwan and Electromagnetic Emanations in Microcontrollers](https://doi.org/10.1145/3133956.3134028) | `microcontroller` |
| 2015 | NDSS | [Firmalice - Automatic Detection of Authentication Bypass Vulnerabilities in Binary Firmware](https://www.ndss-symposium.org/ndss2015/firmalice-automatic-detection-authentication-bypass-vulnerabilities-binary-firmware) | `firmware` |

## Vulnerability discovery

**Core** (8)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2026 | IEEE S&P | [SmuFuzz: Enable Deep System Management Mode Fuzzing in Fully Featured UEFI Runtime Environment](https://doi.org/10.1109/SP63933.2026.00011) | `uefi`, `system management mode` |
| 2025 | NDSS | [A Comprehensive Memory Safety Analysis of Bootloaders](https://www.ndss-symposium.org/ndss-paper/a-comprehensive-memory-safety-analysis-of-bootloaders/) | `bootloader` |
| 2025 | NDSS | [FUZZUER: Enabling Fuzzing of UEFI Interfaces on EDK-2](https://www.ndss-symposium.org/ndss-paper/fuzzuer-enabling-fuzzing-of-uefi-interfaces-on-edk-2/) | `uefi` |
| 2024 | ASE | [STASE: Static Analysis Guided Symbolic Execution for UEFI Vulnerability Signature Generation](https://doi.org/10.1145/3691620.3695543) | `uefi` |
| 2023 | IEEE S&P | [RSFuzzer: Discovering Deep SMI Handler Vulnerabilities in UEFI Firmware with Hybrid Fuzzing](https://doi.org/10.1109/SP46215.2023.10179421) | `uefi` |
| 2022 | IEEE S&P | [Finding SMM Privilege-Escalation Vulnerabilities in UEFI Firmware with Protocol-Centric Static Analysis](https://doi.org/10.1109/SP46214.2022.9833723) | `uefi`, `smm` |
| 2017 | USENIX Security | [BootStomp: On the Security of Bootloaders in Mobile Devices](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/redini) | `bootloader` |
| 2017 | USENIX Security | [fastboot oem vuln: Android Bootloader Vulnerabilities in Vendor Customizations](https://www.usenix.org/conference/woot17/workshop-program/presentation/hay) | `bootloader` |

**Context** (49)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2026 | IEEE S&P | [Bridge: High-Order Taint Vulnerabilities Detection in Linux-Based IoT Firmware](https://doi.org/10.1109/SP63933.2026.00001) | `firmware` |
| 2026 | IEEE S&P | [Stop Starving or Stuffing Me: Boosting Firmware Fuzzing Efficiency with On-Demand Input Delivery](https://doi.org/10.1109/SP63933.2026.00155) | `firmware` |
| 2026 | NDSS | [FirmAgent: Leveraging Fuzzing to Assist LLM Agents with IoT Firmware Vulnerability Discovery](https://www.ndss-symposium.org/ndss-paper/firmagent-leveraging-fuzzing-to-assist-llm-agents-with-iot-firmware-vulnerability-discovery/) | `firmware` |
| 2026 | NDSS | [FirmCross: Detecting Taint-style Vulnerabilities in Modern C-Lua Hybrid Web Services of Linux-based Firmware](https://www.ndss-symposium.org/ndss-paper/firmcross-detecting-taint-style-vulnerabilities-in-modern-c-lua-hybrid-web-services-of-linux-based-firmware/) | `firmware` |
| 2025 | ACM CCS | [Dynamic Vulnerability Patching for Heterogeneous Embedded Systems Using Stack Frame Reconstruction](https://doi.org/10.1145/3719027.3765200) | `embedded system` |
| 2025 | ACM CCS | [Protocol-Aware Firmware Rehosting for Effective Fuzzing of Embedded Network Stacks](https://doi.org/10.1145/3719027.3765125) | `firmware`, `rehosting` |
| 2025 | ACM CCS | [Virtual Reality, Real Problems: A Longitudinal Security Analysis of VR Firmware](https://doi.org/10.1145/3719027.3765102) | `firmware` |
| 2025 | ASE | [DRIFT: Debug-based Trace Inference for Firmware Testing](https://doi.org/10.1109/ASE63991.2025.00211) | `firmware` |
| 2025 | IEEE S&P | [BaseBridge: Bridging the Gap Between Over-the-Air and Emulation Testing for Cellular Baseband Firmware](https://doi.org/10.1109/SP61157.2025.00142) | `firmware` |
| 2025 | IEEE S&P | [Firmrca: Towards Post-Fuzzing Analysis on ARM Embedded Firmware with Efficient Event-Based Fault Localization](https://doi.org/10.1109/SP61157.2025.00002) | `firmware` |
| 2025 | IEEE S&P | [HouseFuzz: Service-Aware Grey-Box Fuzzing for Vulnerability Detection in Linux-Based Firmware](https://doi.org/10.1109/SP61157.2025.00213) | `firmware` |
| 2025 | IEEE S&P | [Stateful Analysis and Fuzzing of Commercial Baseband Firmware](https://doi.org/10.1109/SP61157.2025.00143) | `firmware` |
| 2025 | NDSS | [Mens Sana In Corpore Sano: Sound Firmware Corpora for Vulnerability Research](https://www.ndss-symposium.org/ndss-paper/mens-sana-in-corpore-sano-sound-firmware-corpora-for-vulnerability-research/) | `firmware` |
| 2025 | USENIX Security | [AidFuzzer: Adaptive Interrupt-Driven Firmware Fuzzing via Run-Time State Recognition](https://www.usenix.org/conference/usenixsecurity25/presentation/wang-jianqiang) | `firmware` |
| 2025 | USENIX Security | [From Constraints to Cracks: Constraint Semantic Inconsistencies as Vulnerability Beacons for Embedded Systems](https://www.usenix.org/conference/usenixsecurity25/presentation/zhao) | `embedded system` |
| 2024 | ACM CCS | [Accurate and Efficient Recurring Vulnerability Detection for IoT Firmware](https://doi.org/10.1145/3658644.3670275) | `firmware` |
| 2024 | ACM CCS | [OctopusTaint: Advanced Data Flow Analysis for Detecting Taint-Based Vulnerabilities in IoT/IIoT Firmware](https://doi.org/10.1145/3658644.3690307) | `firmware` |
| 2024 | ACM CCS | [Towards Secure Runtime Auditing of Remote Embedded System Software](https://doi.org/10.1145/3658644.3690856) | `embedded system` |
| 2024 | ICSE | [Semantic-Enhanced Static Vulnerability Detection in Baseband Firmware](https://doi.org/10.1145/3597503.3639158) | `firmware` |
| 2024 | NDSS | [Facilitating Non-Intrusive In-Vivo Firmware Testing with Stateless Instrumentation](https://www.ndss-symposium.org/ndss-paper/facilitating-non-intrusive-in-vivo-firmware-testing-with-stateless-instrumentation/) | `firmware` |
| 2024 | NDSS | [Faster and Better: Detecting Vulnerabilities in Linux-based IoT Firmware with Optimized Reaching Definition Analysis](https://www.ndss-symposium.org/ndss-paper/faster-and-better-detecting-vulnerabilities-in-linux-based-iot-firmware-with-optimized-reaching-definition-analysis/) | `firmware` |
| 2024 | USENIX Security | [Leveraging Semantic Relations in Code and Data to Enhance Taint Analysis of Embedded Systems](https://www.usenix.org/conference/usenixsecurity24/presentation/zhao) | `embedded system` |
| 2024 | USENIX Security | [MultiFuzz: A Multi-Stream Fuzzer For Testing Monolithic Firmware](https://www.usenix.org/conference/usenixsecurity24/presentation/chesser) | `firmware` |
| 2024 | USENIX Security | [Operation Mango: Scalable Discovery of Taint-Style Vulnerabilities in Binary Firmware Services](https://www.usenix.org/conference/usenixsecurity24/presentation/gibbs) | `firmware` |
| 2024 | USENIX Security | [Your Firmware Has Arrived: A Study of Firmware Update Vulnerabilities](https://www.usenix.org/conference/usenixsecurity24/presentation/wu-yuhao) | `firmware` |
| 2023 | ACM CCS | [Poster: Combining Fuzzing with Concolic Execution for IoT Firmware Testing](https://doi.org/10.1145/3576915.3624373) | `firmware` |
| 2023 | ACM CCS | [SHERLOC: Secure and Holistic Control-Flow Violation Detection on Embedded Systems](https://doi.org/10.1145/3576915.3623077) | `embedded system` |
| 2023 | USENIX Security | [Forming Faster Firmware Fuzzers](https://www.usenix.org/conference/usenixsecurity23/presentation/seidel) | `firmware` |
| 2023 | USENIX Security | [Hoedur: Embedded Firmware Fuzzing using Multi-Stream Inputs](https://www.usenix.org/conference/usenixsecurity23/presentation/scharnowski) | `firmware` |
| 2023 | USENIX Security | [UVSCAN: Detecting Third-Party Component Usage Violations in IoT Firmware](https://www.usenix.org/conference/usenixsecurity23/presentation/zhao-binbin) | `firmware` |
| 2022 | ICSE | [$\mu AFL$: Non-intrusive Feedback-driven Fuzzing for Microcontroller Firmware](https://doi.org/10.1145/3510003.3510208) | `firmware`, `microcontroller` |
| 2022 | IEEE S&P | [HEAPSTER: Analyzing the Security of Dynamic Allocators for Monolithic Firmware Images](https://doi.org/10.1109/SP46214.2022.9833610) | `firmware` |
| 2022 | USENIX Security | [Fuzzware: Using Precise MMIO Modeling for Effective Firmware Fuzzing](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski) | `firmware` |
| 2022 | USENIX Security | [Usability and Security of Trusted Platform Module (TPM) Library APIs](https://www.usenix.org/conference/soups2022/presentation/rao) | `tpm` |
| 2021 | ACM CCS | [Snipuzz: Black-box Fuzzing of IoT Firmware via Message Snippet Inference](https://doi.org/10.1145/3460120.3484543) | `firmware` |
| 2021 | FSE | [Towards a workflow for model-based testing of embedded systems](https://doi.org/10.1145/3472672.3473956) | `embedded system` |
| 2021 | USENIX Security | [PASAN: Detecting Peripheral Access Concurrency Bugs within Bare-Metal Embedded Applications](https://www.usenix.org/conference/usenixsecurity21/presentation/kim) | `bare-metal` |
| 2021 | USENIX Security | [Sharing More and Checking Less: Leveraging Common Input Keywords to Detect Bugs in Embedded Systems](https://www.usenix.org/conference/usenixsecurity21/presentation/chen-libo) | `embedded system` |
| 2020 | ACM CCS | [FirmXRay: Detecting Bluetooth Link Layer Vulnerabilities From Bare-Metal Firmware](https://doi.org/10.1145/3372297.3423344) | `firmware`, `bare-metal` |
| 2020 | IEEE S&P | [Karonte: Detecting Insecure Multi-binary Interactions in Embedded Firmware](https://doi.org/10.1109/SP40000.2020.00036) | `firmware` |
| 2020 | USENIX Security | [BigMAC: Fine-Grained Policy Analysis of Android Firmware](https://www.usenix.org/conference/usenixsecurity20/presentation/hernandez) | `firmware` |
| 2020 | USENIX Security | [FIRMSCOPE: Automatic Uncovering of Privilege-Escalation Vulnerabilities in Pre-Installed Apps in Android Firmware](https://www.usenix.org/conference/usenixsecurity20/presentation/elsabagh) | `firmware` |
| 2020 | USENIX Security | [One Exploit to Rule them All? On the Security of Drop-in Replacement and Counterfeit Microcontrollers](https://www.usenix.org/conference/woot20/presentation/obermaier) | `microcontroller` |
| 2020 | USENIX Security | [P2IM: Scalable and Hardware-independent Firmware Testing via Automatic Peripheral Interface Modeling](https://www.usenix.org/conference/usenixsecurity20/presentation/feng) | `firmware` |
| 2020 | USENIX Security | [PARTEMU: Enabling Dynamic Analysis of Real-World TrustZone Software Using Emulation](https://www.usenix.org/conference/usenixsecurity20/presentation/harrison) | `trustzone` |
| 2019 | ACM CCS | [Poster: Fuzzing IoT Firmware via Multi-stage Message Generation](https://doi.org/10.1145/3319535.3363247) | `firmware` |
| 2019 | USENIX Security | [FIRM-AFL: High-Throughput Greybox Fuzzing of IoT Firmware via Augmented Process Emulation](https://www.usenix.org/conference/usenixsecurity19/presentation/zheng) | `firmware` |
| 2018 | USENIX Security | [Inception: System-Wide Security Testing of Real-World Embedded Systems Software](https://www.usenix.org/conference/usenixsecurity18/presentation/corteggiani) | `embedded system` |
| 2017 | ACM CCS | [FirmUSB: Vetting USB Device Firmware using Domain Informed Symbolic Execution](https://doi.org/10.1145/3133956.3134050) | `firmware` |

## Rehosting and emulation

**Context** (13)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2026 | IEEE S&P | [Recovering and Rehosting Mobile Local LLM Conversations and Contexts via Memory Forensics](https://doi.org/10.1109/SP63933.2026.00252) | `rehosting` |
| 2026 | NDSS | [User-Space Dependency-Aware Rehosting for Linux-Based Firmware Binaries](https://www.ndss-symposium.org/ndss-paper/user-space-dependency-aware-rehosting-for-linux-based-firmware-binaries/) | `firmware`, `rehosting` |
| 2025 | USENIX Security | [GDMA: Fully Automated DMA Rehosting via Iterative Type Overlays](https://www.usenix.org/conference/usenixsecurity25/presentation/scharnowski) | `rehosting` |
| 2024 | USENIX Security | [Pandawan: Quantifying Progress in Linux-based Firmware Rehosting](https://www.usenix.org/conference/usenixsecurity24/presentation/angelakopoulos) | `firmware`, `rehosting` |
| 2023 | USENIX Security | [Greenhouse: Single-Service Rehosting of Linux-Based Firmware Binaries in User-Space Emulation](https://www.usenix.org/conference/usenixsecurity23/presentation/tay) | `firmware`, `rehosting` |
| 2022 | ACM CCS | [MetaEmu: An Architecture Agnostic Rehosting Framework for Automotive Firmware](https://doi.org/10.1145/3548606.3559338) | `firmware`, `rehosting` |
| 2022 | ACM CCS | [What Your Firmware Tells You Is Not How You Should Emulate It: A Specification-Guided Approach for Firmware Emulation](https://doi.org/10.1145/3548606.3559386) | `firmware` |
| 2021 | ASE | [FirmGuide: Boosting the Capability of Rehosting Embedded Linux Kernels through Model-Guided Kernel Execution](https://doi.org/10.1109/ASE51524.2021.9678653) | `rehosting` |
| 2021 | IEEE S&P | [DICE: Automatic Emulation of DMA Input Channels for Dynamic Firmware Analysis](https://doi.org/10.1109/SP40001.2021.00018) | `firmware` |
| 2021 | NDSS | [From Library Portability to Para-rehosting: Natively Executing Microcontroller Software on Commodity Hardware](https://www.ndss-symposium.org/ndss-paper/from-library-portability-to-para-rehosting-natively-executing-microcontroller-software-on-commodity-hardware/) | `microcontroller`, `rehosting` |
| 2021 | USENIX Security | [Automatic Firmware Emulation through Invalidity-guided Knowledge Inference](https://www.usenix.org/conference/usenixsecurity21/presentation/zhou) | `firmware` |
| 2021 | USENIX Security | [Jetset: Targeted Firmware Rehosting for Embedded Systems](https://www.usenix.org/conference/usenixsecurity21/presentation/johnson) | `firmware`, `embedded system`, `rehosting` |
| 2020 | USENIX Security | [HALucinator: Firmware Re-hosting Through Abstraction Layer Emulation](https://www.usenix.org/conference/usenixsecurity20/presentation/clements) | `firmware` |

## Defenses, verification and hardening

**Core** (2)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2021 | USENIX Security | [DICE*: A Formally Verified Implementation of DICE Measured Boot](https://www.usenix.org/conference/usenixsecurity21/presentation/tao) | `measured boot` |
| 2019 | NDSS | [Establishing Software Root of Trust Unconditionally](https://www.ndss-symposium.org/ndss-paper/establishing-software-root-of-trust-unconditionally/) | `root of trust` |

**Context** (15)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2025 | IEEE S&P | [PEARTS: Provable Execution in Real-Time Embedded Systems](https://doi.org/10.1109/SP61157.2025.00047) | `embedded system` |
| 2025 | NDSS | [TZ-DATASHIELD: Automated Data Protection for Embedded Systems via Data-Flow-Based Compartmentalization](https://www.ndss-symposium.org/ndss-paper/tz-datashield-automated-data-protection-for-embedded-systems-via-data-flow-based-compartmentalization/) | `embedded system` |
| 2024 | USENIX Security | [FFXE: Dynamic Control Flow Graph Recovery for Embedded Firmware Binaries](https://www.usenix.org/conference/usenixsecurity24/presentation/tsang) | `firmware` |
| 2024 | USENIX Security | [GlobalConfusion: TrustZone Trusted Application 0-Days by Design](https://www.usenix.org/conference/usenixsecurity24/presentation/busch-globalconfusion) | `trustzone` |
| 2023 | IEEE S&P | [EC: Embedded Systems Compartmentalization via Intra-Kernel Isolation](https://doi.org/10.1109/SP46215.2023.10179285) | `embedded system` |
| 2023 | IEEE S&P | [Low-Cost Privilege Separation with Compile Time Compartmentalization for Embedded Systems](https://doi.org/10.1109/SP46215.2023.10179388) | `embedded system` |
| 2022 | USENIX Security | [Holistic Control-Flow Protection on Real-Time Embedded Systems with Kage](https://www.usenix.org/conference/usenixsecurity22/presentation/du) | `embedded system` |
| 2022 | USENIX Security | [PISTIS: Trusted Computing Architecture for Low-end Embedded Systems](https://www.usenix.org/conference/usenixsecurity22/presentation/grisafi) | `embedded system` |
| 2020 | NDSS | [µRAI: Securing Embedded Systems with Return Address Integrity](https://www.ndss-symposium.org/ndss-paper/murai-securing-embedded-systems-with-return-address-integrity/) | `embedded system` |
| 2020 | USENIX Security | [DECAF: Automatic, Adaptive De-bloating and Hardening of COTS Firmware](https://www.usenix.org/conference/usenixsecurity20/presentation/christensen) | `firmware` |
| 2019 | NDSS | [SANCTUARY: ARMing TrustZone with User-space Enclaves](https://www.ndss-symposium.org/ndss-paper/sanctuary-arming-trustzone-with-user-space-enclaves/) | `trustzone` |
| 2017 | IEEE S&P | [One TPM to Bind Them All: Fixing TPM 2.0 for Provably Secure Anonymous Attestation](https://doi.org/10.1109/SP.2017.22) | `tpm` |
| 2017 | IEEE S&P | [Protecting Bare-Metal Embedded Systems with Privilege Overlays](https://doi.org/10.1109/SP.2017.37) | `bare-metal`, `embedded system` |
| 2017 | USENIX Security | [Shedding too much Light on a Microcontroller's Firmware Protection](https://www.usenix.org/conference/woot17/workshop-program/presentation/obermaier) | `firmware`, `microcontroller` |
| 2016 | ACM CCS | [C-FLAT: Control-Flow Attestation for Embedded Systems Software](https://doi.org/10.1145/2976749.2978358) | `embedded system` |

## Other boot- and firmware-related work

**Context** (37)

| Year | Venue | Title | Matched |
|------|-------|-------|---------|
| 2026 | USENIX Security | [Flash [Re]Loaded: Body Bias Injection on Flash Memory](https://www.usenix.org/conference/woot26/presentation/huber) | `flash memory` |
| 2025 | ACM CCS | ['We just did not have that on the embedded system': Insights and Challenges for Securing Microcontroller Systems from the Embedded CTF Competitions](https://doi.org/10.1145/3719027.3765039) | `embedded system`, `microcontroller` |
| 2025 | ICSE | [Moye: A Wallbreaker for Monolithic Firmware](https://doi.org/10.1109/ICSE55347.2025.00053) | `firmware` |
| 2025 | IEEE S&P | [In-Progress: Exploring Tire Pressure Monitoring Systems (TPMS) for Secure Key Generation for Intra-Vehicular Device Authentication](https://doi.org/10.1109/SPW67851.2025.00050) | `tpm` |
| 2025 | USENIX Security | [Kintsugi: Secure Hotpatching for Code-Shadowing Real-Time Embedded Systems](https://www.usenix.org/conference/usenixsecurity25/presentation/mackensen) | `embedded system` |
| 2024 | ACM CCS | [Rust for Embedded Systems: Current State and Open Problems](https://doi.org/10.1145/3658644.3690275) | `embedded system` |
| 2024 | USENIX Security | [CO3: Concolic Co-execution for Firmware](https://www.usenix.org/conference/usenixsecurity24/presentation/liu-changming) | `firmware` |
| 2024 | USENIX Security | [Intellectual Property Exposure: Subverting and Securing Intellectual Property Encapsulation in Texas Instruments Microcontrollers](https://www.usenix.org/conference/usenixsecurity24/presentation/bognar) | `microcontroller` |
| 2024 | USENIX Security | [Unveiling IoT Security in Reality: A Firmware-Centric Journey](https://www.usenix.org/conference/usenixsecurity24/presentation/nino) | `firmware` |
| 2023 | ICSE | [Towards Automated Embedded Systems Programming](https://doi.org/10.1109/ICSE-COMPANION58688.2023.00061) | `embedded system` |
| 2023 | IEEE S&P | [Cryo-Mechanical RAM Content Extraction Against Modern Embedded Systems](https://doi.org/10.1109/SPW59333.2023.00030) | `embedded system` |
| 2022 | ICSE | [Large-scale Security Measurements on the Android Firmware Ecosystem](https://doi.org/10.1145/3510003.3510072) | `firmware` |
| 2022 | IEEE S&P | [A Secure Parser Generation Framework for IoT Protocols on Microcontrollers](https://doi.org/10.1109/SPW54247.2022.9833866) | `microcontroller` |
| 2022 | IEEE S&P | [RT-TEE: Real-time System Availability for Cyber-physical Systems using ARM TrustZone](https://doi.org/10.1109/SP46214.2022.9833604) | `trustzone` |
| 2022 | NDSS | [Building Embedded Systems Like It's 1996](https://www.ndss-symposium.org/ndss-paper/auto-draft-211/) | `embedded system` |
| 2022 | NDSS | [FirmWire: Transparent Dynamic Analysis for Cellular Baseband Firmware](https://www.ndss-symposium.org/ndss-paper/auto-draft-200/) | `firmware` |
| 2022 | USENIX Security | [RapidPatch: Firmware Hotpatching for Real-Time Embedded Devices](https://www.usenix.org/conference/usenixsecurity22/presentation/he-yi) | `firmware` |
| 2022 | USENIX Security | [ReZone: Disarming TrustZone with TEE Privilege Reduction](https://www.usenix.org/conference/usenixsecurity22/presentation/cerdeira) | `trustzone` |
| 2022 | USENIX Security | [Trust Dies in Darkness: Shedding Light on Samsung's TrustZone Keymaster Design](https://www.usenix.org/conference/usenixsecurity22/presentation/shakevsky) | `trustzone` |
| 2021 | ASE | [IFIZZ: Deep-State and Efficient Fault-Scenario Generation to Test IoT Firmware](https://doi.org/10.1109/ASE51524.2021.9678785) | `firmware` |
| 2020 | FSE | [Change impact analysis in Simulink designs of embedded systems](https://doi.org/10.1145/3368089.3417060) | `embedded system` |
| 2020 | USENIX Security | [Firmware Insider: Bluetooth Randomness is Mostly Random](https://www.usenix.org/conference/woot20/presentation/tillmanns) | `firmware` |
| 2020 | USENIX Security | [Silhouette: Efficient Protected Shadow Stacks for Embedded Systems](https://www.usenix.org/conference/usenixsecurity20/presentation/zhou-jie) | `embedded system` |
| 2019 | ACM CCS | [Hardware-Backed Heist: Extracting ECDSA Keys from Qualcomm's TrustZone](https://doi.org/10.1145/3319535.3354197) | `trustzone` |
| 2019 | ACM CCS | [VoltJockey: Breaching TrustZone by Software-Controlled Voltage Manipulation over Multi-core Frequencies](https://doi.org/10.1145/3319535.3354201) | `trustzone` |
| 2019 | ICSE | [Multifaceted automated analyses for variability-intensive embedded systems](https://doi.org/10.1109/ICSE.2019.00092) | `embedded system` |
| 2019 | USENIX Security | [simTPM: User-centric TPM for Mobile Devices](https://www.usenix.org/conference/usenixsecurity19/presentation/chakraborty) | `tpm` |
| 2018 | ICSE | [AutoModel: a domain-specific language for automatic modeling of real-time embedded systems](https://doi.org/10.1145/3183440.3190333) | `embedded system` |
| 2018 | NDSS | [Securing Real-Time Microcontroller Systems through Customized Memory View Switching](https://www.ndss-symposium.org/wp-content/uploads/2018/02/ndss2018_04B-2_Kim_paper.pdf) | `microcontroller` |
| 2018 | USENIX Security | [ACES: Automatic Compartments for Embedded Systems](https://www.usenix.org/conference/usenixsecurity18/presentation/clements) | `embedded system` |
| 2018 | USENIX Security | [BNV: Enabling Scalable Network Experimentation through Bare-metal Network Virtualization](https://www.usenix.org/conference/cset18/presentation/kannan) | `bare-metal` |
| 2017 | ICSE | [Modelling and code generation for real-time embedded systems with UML-RT and papyrus-RT](https://doi.org/10.1109/ICSE-C.2017.168) | `embedded system` |
| 2017 | USENIX Security | [vTZ: Virtualizing ARM TrustZone](https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/hua) | `trustzone` |
| 2016 | ACM CCS | [Scalable Graph-based Bug Search for Firmware Images](https://doi.org/10.1145/2976749.2978370) | `firmware` |
| 2016 | ASE | [Model driven design of heterogeneous synchronous embedded systems](https://doi.org/10.1145/2970276.2970280) | `embedded system` |
| 2016 | NDSS | [Towards Automated Dynamic Analysis for Linux-based Embedded Firmware](http://wp.internetsociety.org/ndss/wp-content/uploads/sites/25/2017/09/towards-automated-dynamic-analysis-linux-based-embedded-firmware.pdf) | `firmware` |
| 2016 | USENIX Security | [fTPM: A Software-Only Implementation of a TPM Chip](https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/raj) | `tpm` |
