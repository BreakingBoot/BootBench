#!/usr/bin/env python3
"""Inventory the security mechanisms each bootloader offers.

BootBench records where bootloaders went wrong and nothing about what defends
them. This is the other half: what each project actually implements.

Two independent sources, because neither alone is honest:

* **Declared features**, from source. Whether a project *supports* Secure Boot,
  measured boot, signature verification or rollback protection is visible in
  its build configuration and code, and is a property of the project.
* **Binary mitigations**, from a built artifact. Whether NX, RELRO, PIE, stack
  protector or FORTIFY are actually *on* is a property of one build, not of the
  project, and needs `readelf` and `nm` -- no other tooling.

The distinction matters: a bootloader can implement Secure Boot and still
compile without a stack protector, and the two say different things about its
security posture.

Usage
-----
    python3 scan_defenses.py --root .. --output ../oss-bootloaders/defenses.json
    python3 scan_defenses.py --root .. --binary path/to/built.efi
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

# What to look for in source, and what each grouping means. Patterns are
# matched against build configuration and source identifiers, so they are
# evidence that a project *has* the feature, not that a given build enables it.
FEATURES: dict[str, dict[str, Any]] = {
    "secure_boot": {
        "label": "Secure Boot / verified boot",
        "patterns": [r"SECURE_BOOT", r"secure[_ ]boot", r"VERIFIED_BOOT", r"verified[_ ]boot"],
    },
    "signature_verification": {
        "label": "Image signature verification",
        "patterns": [r"verify_signature", r"SIGNATURE_VERIF", r"AuthenticodeVerify",
                     r"pkcs7_verify", r"rsa_verify", r"ecdsa_verify", r"VERIFY_SIG"],
    },
    "measured_boot": {
        "label": "Measured boot / TPM",
        # TPM appears as a config symbol far more often than as prose, so
        # anchor on the symbol forms rather than the bare acronym.
        "patterns": [r"CONFIG_TPM", r"measured[_ ]boot", r"PCR_?EXTEND", r"tpm2?_pcr",
                     r"TPM2_", r"tpm2?_extend"],
    },
    "rollback_protection": {
        "label": "Rollback / anti-downgrade",
        "patterns": [r"ROLLBACK", r"anti[_ ]?rollback", r"SECURITY_COUNTER",
                     r"downgrade[_ ]protect"],
    },
    "encryption": {
        "label": "Image encryption",
        "patterns": [r"ENCRYPTED_IMAGE", r"IMAGE_ENCRYPT", r"aes_decrypt", r"DECRYPT_IMAGE"],
    },
    "stack_protector": {
        "label": "Stack protector (declared)",
        "patterns": [r"STACK_?PROTECTOR", r"fstack-protector"],
    },
    "fortify": {
        "label": "FORTIFY_SOURCE (declared)",
        "patterns": [r"FORTIFY_SOURCE"],
    },
    "cfi": {
        "label": "Control-flow integrity",
        # NOT bare "CFI": in bootloaders that overwhelmingly means Common Flash
        # Interface, the NOR flash standard. It matched u-boot's MIPS Kconfig
        # and wolfBoot's NXP flash HAL, neither of which is control-flow
        # integrity. Same trap as the bare "dos" vulnerability keyword.
        "patterns": [r"fsanitize=cfi", r"CFI_CLANG", r"SHADOW_CALL_STACK",
                     r"cf_protection", r"control[- ]flow[- ]integrity",
                     r"\bIBT\b", r"branch[- ]target[- ]identification", r"\bBTI\b"],
    },
    "aslr": {
        "label": "Load-address randomisation",
        "patterns": [r"\bASLR\b", r"RANDOMIZE_BASE", r"randomize[_ ]load"],
    },
}

# Files worth reading. Bootloaders keep their security switches in build
# configuration far more often than in source, and scanning whole trees of
# vendored third-party code produces noise rather than signal.
CONFIG_GLOBS = ("Kconfig*", "*.mk", "Makefile*", "*.dsc", "*.dec", "defconfig",
                "*config*", "*.cmake", "CMakeLists.txt")
SOURCE_GLOBS = ("*.c", "*.h", "*.S", "*.rs", "*.py")
MAX_FILES = 4000


def scan_source(repo: Path) -> dict[str, Any]:
    """Look for declared security features in a bootloader's own tree."""
    compiled = {k: [re.compile(p, re.IGNORECASE) for p in v["patterns"]]
                for k, v in FEATURES.items()}
    hits: dict[str, int] = Counter()
    evidence: dict[str, str] = {}

    paths: list[Path] = []
    for pattern in CONFIG_GLOBS + SOURCE_GLOBS:
        paths.extend(repo.rglob(pattern))
        if len(paths) > MAX_FILES:
            break
    scanned = 0
    for path in paths[:MAX_FILES]:
        if not path.is_file() or path.stat().st_size > 512_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        scanned += 1
        for feature, patterns in compiled.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    hits[feature] += 1
                    evidence.setdefault(
                        feature, f"{path.relative_to(repo)}: {match.group(0)[:40]}")
                    break
    return {"files_scanned": scanned,
            "features": {k: {"hits": hits[k], "evidence": evidence.get(k)}
                         for k in FEATURES if hits[k]}}


def scan_binary(path: Path) -> dict[str, Any]:
    """Mitigations actually enabled in one built artifact."""
    def run(*args: str) -> str:
        try:
            return subprocess.run(args, capture_output=True, text=True, check=False).stdout
        except FileNotFoundError:
            return ""

    headers = run("readelf", "-lW", str(path))
    dynamic = run("readelf", "-dW", str(path))
    elf_head = run("readelf", "-hW", str(path))
    symbols = run("nm", "-D", str(path)) + run("nm", str(path))

    if not headers and not elf_head:
        return {"format": "not an ELF (PE/COFF images need a different reader)"}

    gnu_stack = [l for l in headers.splitlines() if "GNU_STACK" in l]
    return {
        "format": "elf",
        "nx": bool(gnu_stack) and "RWE" not in gnu_stack[0],
        "relro": "GNU_RELRO" in headers,
        "bind_now": "BIND_NOW" in dynamic or "NOW" in dynamic,
        "pie": "DYN (" in elf_head or "Position-Independent" in elf_head,
        "stack_protector": "__stack_chk" in symbols,
        "fortify_source": "_chk@" in symbols or "__printf_chk" in symbols,
    }


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=here.parent)
    parser.add_argument("--output", type=Path, help="JSON inventory to write")
    parser.add_argument("--markdown", type=Path, help="also write a summary table")
    parser.add_argument("--binary", type=Path, action="append", default=[],
                        help="also report mitigations for a built artifact (repeatable)")
    parser.add_argument("--only", help="scan a single bootloader by name")
    args = parser.parse_args()

    root = args.root.resolve()
    gitmodules = root / "oss-bootloaders" / ".gitmodules"
    parser_cfg = configparser.ConfigParser()
    parser_cfg.read_string(gitmodules.read_text(encoding="utf-8"))
    paths = [parser_cfg.get(s, "path") for s in parser_cfg.sections()
             if parser_cfg.has_option(s, "path")]

    inventory: dict[str, Any] = {"bootloaders": {}, "binaries": {}}
    scanned = skipped = 0
    for rel in sorted(paths):
        btype, _, name = rel.partition("/")
        if args.only and name != args.only:
            continue
        repo = root / "oss-bootloaders" / rel
        if not (repo / ".git").exists():
            skipped += 1
            continue
        result = scan_source(repo)
        result["type"] = btype
        inventory["bootloaders"][name] = result
        scanned += 1
        found = ", ".join(sorted(result["features"])) or "none detected"
        print(f"  {name:28s} {found}")

    for binary in args.binary:
        if binary.is_file():
            inventory["binaries"][binary.name] = scan_binary(binary)

    print(f"\n[INFO] scanned {scanned} bootloaders, skipped {skipped} not checked out")
    coverage = Counter()
    for entry in inventory["bootloaders"].values():
        for feature in entry["features"]:
            coverage[feature] += 1
    print("[INFO] feature coverage across the corpus:")
    for feature, count in coverage.most_common():
        print(f"         {count:3d}/{scanned}  {FEATURES[feature]['label']}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
        print(f"[INFO] inventory written to {args.output}")
    if args.markdown:
        args.markdown.write_text(render(inventory, scanned), encoding="utf-8")
        print(f"[INFO] summary written to {args.markdown}")
    return 0


def render(inventory: dict[str, Any], scanned: int) -> str:
    boots = inventory["bootloaders"]
    keys = ["secure_boot", "signature_verification", "measured_boot",
            "rollback_protection", "encryption", "stack_protector", "cfi"]
    short = {"secure_boot": "Secure Boot", "signature_verification": "Sig verify",
             "measured_boot": "Measured", "rollback_protection": "Rollback",
             "encryption": "Encrypt", "stack_protector": "Stack prot", "cfi": "CFI"}
    lines = ["# Bootloader security mechanisms", "",
             "What each bootloader in the corpus *implements*, found by scanning its build",
             "configuration and source. A tick means the project has the feature, not that a",
             "given build enables it — those are different claims, and the binary table below",
             "is the one that reflects a real build.", "",
             "Generated by `tools/scan_defenses.py`.", "",
             "| Bootloader | Type | " + " | ".join(short[k] for k in keys) + " |",
             "|---|---|" + "---|" * len(keys)]
    for name, entry in sorted(boots.items()):
        row = [f"`{name}`", entry["type"]]
        row += ["yes" if k in entry["features"] else "—" for k in keys]
        lines.append("| " + " | ".join(row) + " |")

    coverage = Counter()
    for entry in boots.values():
        for feature in entry["features"]:
            coverage[feature] += 1
    lines += ["", "## Coverage", "", "| Mechanism | Bootloaders |", "|---|---:|"]
    for key in keys:
        lines.append(f"| {FEATURES[key]['label']} | {coverage[key]} of {scanned} |")

    if inventory.get("binaries"):
        lines += ["", "## Mitigations in built artifacts", "",
                  "Properties of one build, read with `readelf` and `nm`.", "",
                  "| Artifact | NX | RELRO | BIND_NOW | PIE | Stack prot | FORTIFY |",
                  "|---|---|---|---|---|---|---|"]
        for name, b in sorted(inventory["binaries"].items()):
            if b.get("format") != "elf":
                lines.append(f"| `{name}` | " + " | ".join(["—"] * 6) + " |")
                continue
            cells = ["yes" if b.get(k) else "no" for k in
                     ("nx", "relro", "bind_now", "pie", "stack_protector", "fortify_source")]
            lines.append(f"| `{name}` | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
