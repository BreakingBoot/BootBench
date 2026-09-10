"""Classification rules shared by the BootBench collection tools.

The bootloader-type keyword lists below were previously reachable only as
inline shell arguments inside ``bootloader_cve_db/.github/workflows/main.yml``.
Lifting them here makes the classification that produced the published dataset
reviewable, testable, and reusable.

The lists are reproduced verbatim from that workflow.  ``classify_cves.py``
applies them with word-boundary matching and first-match-wins ordering, which
reproduces the published ``type<N>-keyword-breakdown.json`` counts exactly for
all three types (734 / 301 / 122 CVEs).  Do not reorder a list without
re-running ``validate_dataset.py --check classification``: the order decides
which keyword a multi-keyword CVE is attributed to.
"""

from __future__ import annotations

import re
from typing import Iterable, Sequence

# --------------------------------------------------------------------------
# Bootloader-type classification (used against CVE descriptions)
# --------------------------------------------------------------------------

TYPE1_INCLUDE: Sequence[str] = (
    "SMM", "System Management Mode", "pc firmware", "uefi", "bios", "lakebios",
    "edk2", "firmware-open", "open firmware", "libreboot",
    "low-level bootloader", "low level bootloader", "openfirmware",
    "slimbootloader", "slimboot", "seabios", "coreboot", "bootloader firmware",
    "server firmware", "boot services",
)

TYPE2_INCLUDE: Sequence[str] = (
    "cloverbootloader", "clover bootloader", "iboot", "opencore", "depthcharge",
    "easyboot", "ipxe", "little kernel", "lk", "grub2", "windows boot manager",
    "aboot", "android bootloader", "limine", "shim", "tboot", "t-boot",
    "refind", "skiboot", "pxelinux", "systemd-boot", "systemd boot",
    "bootloader", "boot loader", "boot-loader", "grub", "bootmanager", "pxe",
    "network boot", "boot manager", "os loader",
)

TYPE3_INCLUDE: Sequence[str] = (
    "mcuboot", "tf-a", "arm-trusted-firmware", "arm trusted firmware",
    "barebox", "imbootloader", "openblt", "redboot", "uboot", "u-boot",
    "wolfboot", "monolithic", "bootimage", "boot image", "bootrom",
    "embedded firmware", "firmware embedded", "embedded boot", "boot rom",
    "IoT firmware", "device firmware",
)

# Type 1 excludes the Type 2 vocabulary so staged-boot CVEs land in Type 2.
TYPE1_EXCLUDE: Sequence[str] = (
    "linux kernel", "cloverbootloader", "clover bootloader", "iboot",
    "opencore", "depthcharge", "easyboot", "ipxe", "little kernel", "lk",
    "grub2", "windows boot manager", "system center configuration manager",
    "sccm", "limine", "shim", "tboot", "t-boot", "refind", "skiboot",
    "open-iscsi", "iscsi", "systemd-boot", "systemd", "bootloader",
    "boot loader", "boot-loader", "grub", "bootmanager", "pxe", "network boot",
    "boot manager", "os loader",
)

TYPE2_EXCLUDE: Sequence[str] = ("linux kernel", "rom", "bootrom")

# Type 3 excludes everything claimed by Types 1 and 2, so a monolithic
# bootloader only matches when no staged-boot vocabulary is present.
TYPE3_EXCLUDE: Sequence[str] = tuple(
    dict.fromkeys(("linux kernel",) + tuple(TYPE1_INCLUDE) + tuple(TYPE1_EXCLUDE[1:]))
)

BOOTLOADER_TYPES = {
    "type1": (TYPE1_INCLUDE, TYPE1_EXCLUDE),
    "type2": (TYPE2_INCLUDE, TYPE2_EXCLUDE),
    "type3": (TYPE3_INCLUDE, TYPE3_EXCLUDE),
}

TYPE_LABELS = {
    "type1": "Firmware bootloader",
    "type2": "OS bootloader",
    "type3": "Monolithic bootloader",
}


# Trailing plural, allowed after a keyword's final word.  Word boundaries alone
# would drop "Prevent buffer overflows", "Fix race conditions" and "caused by
# NULL pointers" -- real fixes that the old substring matcher did catch.  It
# stays tight enough to keep rejecting "exploitation" for "exploit".
_PLURAL = r"(?:e?s)?"


def compile_keywords(keywords: Iterable[str],
                     allow_plural: bool = False) -> list[tuple[str, re.Pattern[str]]]:
    """Compile keywords into word-boundary, case-insensitive patterns.

    Word boundaries matter: plain substring matching credits "boot services"
    to any text containing "reboot services", and is what makes the commit
    miner's ``dos`` keyword match "TODOs".  See tools/README.md.

    ``allow_plural`` additionally accepts a trailing "s"/"es" on the keyword's
    last word.  It is used for commit-message keywords, where "buffer
    overflows" is the same finding as "buffer overflow", and deliberately NOT
    for CVE type classification, which must keep reproducing the published
    keyword breakdown exactly.
    """
    suffix = _PLURAL if allow_plural else ""
    return [
        (kw.lower(), re.compile(r"\b" + re.escape(kw) + suffix + r"\b", re.IGNORECASE))
        for kw in keywords
    ]


def first_match(text: str, patterns: Sequence[tuple[str, re.Pattern[str]]]) -> str | None:
    """Return the first keyword (in list order) that matches ``text``."""
    for keyword, pattern in patterns:
        if pattern.search(text):
            return keyword
    return None


def all_matches(text: str, patterns: Sequence[tuple[str, re.Pattern[str]]]) -> list[str]:
    """Return every keyword that matches ``text``, in list order."""
    return [keyword for keyword, pattern in patterns if pattern.search(text)]


# --------------------------------------------------------------------------
# Vulnerability-keyword matching (used against git commit messages)
# --------------------------------------------------------------------------

# Reproduced from bootloader_vuln_commits/extract_cve_commits.py, with two
# corrections that are documented and measured in tools/README.md:
#   * the bare acronym "dos" is gone -- word-bounded, it still matched 267
#     commits, every one of them about DOS the operating system ("DOS header",
#     "dos partition table") and none about denial of service.  The acronym is
#     now matched case-sensitively as DoS, alongside the spelled-out phrase.
#   * matching is word-bounded rather than substring, which drops the
#     "TODOs"/"msdos"/"FreeDOS" family of false positives.
VULNERABILITY_KEYWORDS: Sequence[str] = (
    "buffer overflow", "use-after-free", "use after free", "race condition",
    "privilege escalation", "heap corruption", "memory corruption",
    "arbitrary code execution", "denial of service", "integer overflow",
    "double free", "null pointer", "out-of-bounds", "out of bounds",
    "cross-site scripting", "xss", "sql injection", "vulnerability",
    "vulnerabilities", "vulnerable", "vuln", "exploit", "security flaw",
    "security issue", "stack consumption", "crafted squashfs filesystem",
)

# Patterns that must keep their case to stay meaningful.
CASE_SENSITIVE_VULN_KEYWORDS: Sequence[str] = ("DoS",)

CVE_PATTERN = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)


def compile_vulnerability_patterns() -> list[tuple[str, re.Pattern[str]]]:
    """Compile the vulnerability keyword set used to mine commit messages."""
    patterns = compile_keywords(VULNERABILITY_KEYWORDS, allow_plural=True)
    patterns += [
        (kw, re.compile(r"\b" + re.escape(kw) + r"\b"))
        for kw in CASE_SENSITIVE_VULN_KEYWORDS
    ]
    return patterns


# --------------------------------------------------------------------------
# Literature search (used against paper titles)
# --------------------------------------------------------------------------

# The SoK surveyed the top four security venues (IEEE S&P, ACM CCS, USENIX
# Security, NDSS) and four software-engineering venues (ICSE, FSE, ASE,
# OOPSLA) for tools and techniques applicable to bootloaders.  These are the
# terms ``collect_papers.py`` greps titles with.
#
# CORE terms name the boot chain directly and are high precision.  CONTEXT
# terms are broader -- "firmware" alone pulls in IoT and peripheral work -- but
# the SoK's tool survey draws on exactly that literature, so they are kept and
# every hit records which term matched.  Use --core-only to drop them.
PAPER_KEYWORDS_CORE: Sequence[str] = (
    "bootloader", "boot loader", "bootkit", "secure boot", "verified boot",
    "measured boot", "trusted boot", "boot process", "boot chain",
    "chain of trust", "root of trust", "uefi", "bios", "smm",
    "system management mode", "coreboot", "u-boot", "uboot", "grub", "edk2",
    "bootrom", "boot rom", "mcuboot", "trusted firmware", "boot image",
    "pre-boot", "early boot", "power-on",
)
# "bootstrap" is deliberately absent: every title it matched was FHE
# bootstrapping or the machine-learning sense ("Bootstrap Conversational
# Agents"), never the boot chain.  Same failure mode as "dos" matching
# "TODOs" in commit messages.

PAPER_KEYWORDS_CONTEXT: Sequence[str] = (
    "firmware", "bare-metal", "bare metal", "embedded system",
    "microcontroller", "rehosting", "trustzone", "tpm", "flash memory",
)
# "attestation", "rollback" and "peripheral" were dropped: their hits were
# dominated by TLS, blockchain and enclave work with no boot-chain content.

# Venue -> DBLP stream.  dblp types yearOfPublication as xsd:gYear, so a year
# filter has to cast through a string (xsd:integer(?y) silently matches
# nothing).
PAPER_VENUES: dict[str, str] = {
    "IEEE S&P": "conf/sp",
    "ACM CCS": "conf/ccs",
    "USENIX Security": "conf/uss",
    "NDSS": "conf/ndss",
    "ICSE": "conf/icse",
    "FSE": "conf/sigsoft",
    "ASE": "conf/kbse",
    "OOPSLA": "conf/oopsla",
}

SECURITY_VENUES = ("IEEE S&P", "ACM CCS", "USENIX Security", "NDSS")
SE_VENUES = ("ICSE", "FSE", "ASE", "OOPSLA")

# What a paper contributes, decided from its title.  First match in this order
# wins, so the list is ordered from most specific claim to least: a title that
# both systematizes and analyses is a systematization.  Rules rather than hand
# curation, so the papers index can be regenerated when the search is re-run.
PAPER_CONTRIBUTIONS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("systematization", "Systematization and measurement",
     ("sok", "systematic literature", "systematic review", "survey", "empirically measuring",
      "measurement study", "large-scale study", "an analysis of", "understanding",
      "characterizing", "demystifying", "years of")),
    ("attack", "Attacks and case studies",
     ("attack", "attacking", "breaking", "defeating", "bypass", "bypassing", "exploiting",
      "exploitation", "bootkit", "rootkit", "backdoor", "hijack", "compromis",
      "achilles", "injection attack", "fault injection", "glitch", "side channel",
      "side-channel", "leakage", "stealthy", "malicious", "abusing")),
    ("discovery", "Vulnerability discovery",
     ("fuzz", "fuzzing", "symbolic execution", "static analysis", "taint", "detect",
      "detecting", "detection", "discovering", "finding", "identifying", "uncovering",
      "bug hunting", "vulnerability", "vulnerabilities", "sanitiz", "testing",
      "test generation", "analysis of", "auditing", "security of",
      "security analysis", "security assessment")),
    ("rehosting", "Rehosting and emulation",
     ("rehosting", "rehost", "emulation", "emulating", "harness", "peripheral modeling",
      "firmware emulation", "virtual prototype")),
    ("defense", "Defenses, verification and hardening",
     ("verified", "verification", "formally", "formal", "proof", "provable", "hardening",
      "mitigation", "mitigating", "defense", "defence", "protecting", "protection",
      "isolation", "integrity", "attestation", "enclave", "sandbox", "compartmental",
      "secure boot", "measured boot", "root of trust", "chain of trust", "trusted",
      "recovery", "patching", "update")),
)

PAPER_CONTRIBUTION_FALLBACK = ("other", "Other boot- and firmware-related work")


# --------------------------------------------------------------------------
# Attack surfaces
# --------------------------------------------------------------------------

# The six surfaces the SoK defines, split into hardware (the attacker has
# physical access) and software (the attacker reaches the bootloader through an
# interface it exposes). Ordered most specific first: a CVE about an SMI
# handler is post-boot, not merely "a firmware bug".
#
# Terms are matched with word boundaries. Bare acronyms that mean something
# else in this domain are avoided -- "DMA" is safe, "CFI" and "dos" are not.
ATTACK_SURFACES: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("SAS3", "software", "Post-boot features",
     ("smm", "system management mode", "smi handler", "smi ", "smram",
      "runtime service", "runtime services", "post-boot", "after exitbootservices",
      "exitbootservices", "system management interrupt", "smbase")),
    ("SAS1", "software", "Remote access",
     ("network boot", "netboot", "pxe", "pxelinux", "tftp", "dhcp", "bootp",
      "iscsi", "http boot", "httpboot", "http response", "http request",
      "http header", "ipv4", "ipv6", "remote attacker", "remote code execution",
      "remotely", "network stack", "network packet", "udp", "tcp/ip")),
    ("SAS4", "software", "Boot-time features",
     ("boot menu", "grub shell", "uefi shell", "efi shell", "command line",
      "interactive shell", "recovery mode", "boot prompt", "rescue mode",
      "fastboot", "download mode", "unlock command")),
    ("SAS2", "software", "Persistent data source",
     ("grub.cfg", "grub configuration", "boot configuration data", "bcd",
      "uefi variable", "nvram", "efi variable", "setvariable", "getvariable",
      "boot logo", "splash", "bmp image", "acpi table", "device tree",
      "partition table", "file system", "filesystem", "squashfs", "ext4",
      "boot image", "configuration file", "environment variable")),
    ("HAS2", "hardware", "External hardware",
     ("usb", "dma", "thunderbolt", "pci express", "pcie", "firewire",
      "external device", "removable media", "sd card", "peripheral device",
      "malicious device")),
    ("HAS1", "hardware", "Invasive hardware",
     ("spi flash", "flash chip", "jtag", "debug port", "chip-off", "soldering",
      "bus pirate", "voltage glitch", "fault injection", "electromagnetic",
      "side-channel", "power analysis", "physical access to the flash")),
)


def compile_attack_surfaces() -> list[tuple[str, str, str, re.Pattern[str]]]:
    """Compile the surface definitions into (id, kind, label, pattern)."""
    compiled = []
    for surface_id, kind, label, terms in ATTACK_SURFACES:
        alternation = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
        compiled.append((surface_id, kind, label,
                         re.compile(r"\b(?:" + alternation + r")", re.IGNORECASE)))
    return compiled


# --------------------------------------------------------------------------
# CWE matching
# --------------------------------------------------------------------------

# Deterministic replacement for the RapidFuzz ``token_set_ratio`` matching in
# extract_cve_commits.py.  token_set_ratio scores 100 whenever a CWE name's
# tokens are a subset of the message's, so it labelled "Bump version to 15.8"
# as CWE-680 (Integer Overflow to Buffer Overflow) and "roms: only support
# SeaBIOS/SeaGRUB on x86" as CWE-260 (Password in Configuration File).
#
# Each entry maps a CWE to phrases that actually appear in fix commits.  A
# commit is tagged only on an explicit phrase hit, so precision is the default
# and recall can be extended by adding aliases here.
CWE_ALIASES: dict[str, tuple[str, tuple[str, ...]]] = {
    "119": ("Improper Restriction of Operations within the Bounds of a Memory Buffer",
            ("buffer overflow", "buffer overrun", "memory corruption", "heap corruption")),
    "120": ("Buffer Copy without Checking Size of Input",
            ("unbounded copy", "strcpy overflow", "classic buffer overflow")),
    "125": ("Out-of-bounds Read",
            ("out-of-bounds read", "out of bounds read", "oob read", "overread",
             "read past the end", "buffer over-read")),
    "134": ("Use of Externally-Controlled Format String",
            ("format string",)),
    "190": ("Integer Overflow or Wraparound",
            ("integer overflow", "integer wraparound", "arithmetic overflow")),
    "191": ("Integer Underflow", ("integer underflow",)),
    "193": ("Off-by-one Error", ("off-by-one", "off by one")),
    "252": ("Unchecked Return Value", ("unchecked return value",)),
    "362": ("Race Condition", ("race condition", "toctou", "time-of-check")),
    "367": ("Time-of-check Time-of-use Race Condition",
            ("time-of-check time-of-use", "toctou")),
    "369": ("Divide By Zero", ("divide by zero", "division by zero")),
    "400": ("Uncontrolled Resource Consumption",
            ("resource exhaustion", "uncontrolled resource consumption")),
    "401": ("Missing Release of Memory after Effective Lifetime",
            ("memory leak", "leaks memory")),
    "415": ("Double Free", ("double free", "double-free")),
    "416": ("Use After Free", ("use-after-free", "use after free", "uaf")),
    "457": ("Use of Uninitialized Variable",
            ("uninitialized variable", "uninitialised variable", "use of uninitialized")),
    "476": ("NULL Pointer Dereference",
            ("null pointer dereference", "null-pointer dereference", "null deref",
             "nullptr dereference")),
    "617": ("Reachable Assertion", ("reachable assertion",)),
    "681": ("Incorrect Conversion between Numeric Types",
            ("integer truncation", "incorrect cast", "sign extension bug")),
    "755": ("Improper Handling of Exceptional Conditions",
            ("improper error handling", "unhandled error")),
    "787": ("Out-of-bounds Write",
            ("out-of-bounds write", "out of bounds write", "oob write",
             "buffer overflow write", "write past the end", "stack smashing")),
    "20":  ("Improper Input Validation",
            ("improper input validation", "missing input validation",
             "insufficient validation", "unvalidated input")),
    "22":  ("Path Traversal", ("path traversal", "directory traversal")),
    "287": ("Improper Authentication",
            ("authentication bypass", "improper authentication")),
    "295": ("Improper Certificate Validation",
            ("certificate validation", "improper certificate")),
    "347": ("Improper Verification of Cryptographic Signature",
            ("signature verification", "improper signature", "verify the signature",
             "secure boot bypass")),
    "665": ("Improper Initialization", ("improper initialization", "uninitialized memory")),
    "732": ("Incorrect Permission Assignment for Critical Resource",
            ("incorrect permission", "world-writable")),
    "269": ("Improper Privilege Management",
            ("privilege escalation", "escalation of privilege")),
}


def compile_cwe_patterns() -> list[tuple[str, str, re.Pattern[str]]]:
    """Compile the CWE alias table into (id, name, pattern) triples."""
    compiled = []
    for cwe_id, (name, aliases) in CWE_ALIASES.items():
        alternation = "|".join(re.escape(a) for a in aliases)
        compiled.append(
            (cwe_id, name,
             re.compile(r"\b(?:" + alternation + r")" + _PLURAL + r"\b", re.IGNORECASE))
        )
    return compiled
