#!/usr/bin/env python3
"""Resolve each CVE to the corpus bootloaders it affects.

The classifier answers "is this CVE about *a* bootloader" and stops. Nothing
records *which* one, so a researcher cannot select the CVEs for the bootloader
they are studying, and unrelated entries are indistinguishable from real ones:
containerd, OpenStack Ironic and Xen all currently sit in the database beside
genuine entries like barebox.

This adds a ``bootloaders`` field per CVE, resolved from three signals in
descending order of trust:

* ``affected`` — the vendor/product list in the CVE record names the project.
* ``reference`` — a reference URL points at the project's repository.
* ``description`` — the description names the project.

Each match records which signal produced it, so a consumer can filter on
confidence rather than trusting a single opaque label. A CVE that resolves to
nothing gets an empty list, which is a useful answer in itself: 41% of records
carry no usable affected-product data at all.

Usage
-----
    python3 map_cves_to_bootloaders.py --root .. --write
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

TYPES = ("type1", "type2", "type3")

# Names a CVE record is likely to use that differ from the submodule directory.
ALIASES: dict[str, tuple[str, ...]] = {
    "edk2": ("edk2", "edk ii", "edk-ii", "tianocore", "uefi reference implementation"),
    "grub": ("grub", "grub2", "grub 2", "gnu grub"),
    "u-boot": ("u-boot", "uboot", "das u-boot"),
    "shim": ("shim",),
    "systemd": ("systemd", "systemd-boot", "gummiboot"),
    "coreboot": ("coreboot",),
    "seabios": ("seabios",),
    "barebox": ("barebox",),
    "mcuboot": ("mcuboot",),
    "arm-trusted-firmware": ("arm trusted firmware", "trusted firmware-a", "tf-a",
                             "arm-trusted-firmware"),
    "trusted-firmware-m": ("trusted firmware-m", "tf-m", "trusted-firmware-m"),
    "lk": ("little kernel", "lk bootloader"),
    "lk2nd": ("lk2nd",),
    "ipxe": ("ipxe",),
    "syslinux": ("syslinux", "isolinux", "pxelinux"),
    "opensbi": ("opensbi", "open sbi"),
    "skiboot": ("skiboot",),
    "hostboot": ("hostboot",),
    "petitboot": ("petitboot",),
    "slimbootloader": ("slim bootloader", "slimbootloader"),
    "openbios": ("openbios",),
    "wolfBoot": ("wolfboot",),
    "rustBoot": ("rustboot",),
    "mu_basecore": ("project mu", "mu_basecore"),
    "OpenCorePkg": ("opencore", "opencorepkg"),
    "CloverBootloader": ("clover", "cloverbootloader"),
    "refind": ("refind", "rEFInd"),
    "limine": ("limine bootloader", "limine"),
    "depthcharge": ("depthcharge",),
    "kexec-tools": ("kexec-tools", "kexec tools"),
    "open-iscsi": ("open-iscsi", "iscsi initiator"),
    "u-root": ("u-root",),
    "aboot": ("aboot", "android bootloader"),
    "tboot-mirror": ("tboot", "trusted boot"),
    "optiboot": ("optiboot",),
    "openblt": ("openblt",),
    "redboot": ("redboot",),
    "oreboot": ("oreboot",),
    "lbmk": ("libreboot", "lbmk"),
}


def corpus_bootloaders(root: Path) -> dict[str, str]:
    """Map bootloader name -> type from the corpus .gitmodules."""
    parser = configparser.ConfigParser()
    parser.read_string((root / "oss-bootloaders" / ".gitmodules").read_text(encoding="utf-8"))
    out = {}
    for section in parser.sections():
        if not parser.has_option(section, "path"):
            continue
        path = parser.get(section, "path")
        btype, _, name = path.partition("/")
        out[name] = btype
    return out


# Corpus directory names that are ordinary words. Matching them bare against a
# CVE description is meaningless -- "firmware" hit 388 CVEs and "bootloader"
# 207, none of which says anything about the Meshtastic or rust-osdev projects
# those directories actually hold. They resolve only through an explicit alias.
GENERIC_NAMES = {"firmware", "bootloader", "harmony", "openbl", "linuxboot",
                 "easyboot", "quibble", "chameleon", "limine"}


def build_patterns(names: dict[str, str]) -> list[tuple[str, re.Pattern[str]]]:
    """Word-bounded patterns per bootloader, aliases included.

    A bare name is used only when it is distinctive. Names under four
    characters ("lk") and ordinary words ("firmware") need an explicit alias,
    or they match text that has nothing to do with the project.
    """
    patterns = []
    for name in names:
        terms = set(ALIASES.get(name, ()))
        if len(name) >= 4 and name.lower() not in GENERIC_NAMES:
            terms.add(name.lower())
        if not terms:
            continue
        alternation = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
        patterns.append((name, re.compile(r"\b(?:" + alternation + r")\b", re.IGNORECASE)))
    return patterns


def resolve(entry: dict[str, Any], patterns) -> list[dict[str, str]]:
    """Match one CVE against the corpus, recording which signal matched."""
    affected_text = " ".join(
        f"{a.get('vendor', '')} {a.get('product', '')}" for a in entry.get("affected") or [])
    reference_text = " ".join(r.get("url", "") for r in entry.get("references") or [])
    description = entry.get("description", "")

    hits: dict[str, str] = {}
    for name, pattern in patterns:
        if pattern.search(affected_text):
            hits[name] = "affected"
        elif pattern.search(reference_text):
            hits.setdefault(name, "reference")
        elif pattern.search(description):
            hits.setdefault(name, "description")
    order = {"affected": 0, "reference": 1, "description": 2}
    return [{"bootloader": n, "matched_on": s}
            for n, s in sorted(hits.items(), key=lambda kv: (order[kv[1]], kv[0]))]


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=here.parent)
    parser.add_argument("--write", action="store_true",
                        help="write the bootloaders field back into the results files")
    args = parser.parse_args()

    root = args.root.resolve()
    names = corpus_bootloaders(root)
    patterns = build_patterns(names)
    print(f"[INFO] {len(patterns)} corpus bootloaders matchable by name or alias")

    per_signal: Counter = Counter()
    per_bootloader: Counter = Counter()
    resolved = total = 0

    for btype in TYPES:
        path = root / "bootloader_cve_db" / btype / f"{btype}-results.json"
        results = json.loads(path.read_text(encoding="utf-8"))
        for entry in results.values():
            total += 1
            hits = resolve(entry, patterns)
            entry["bootloaders"] = hits
            if hits:
                resolved += 1
                per_signal[hits[0]["matched_on"]] += 1
                for h in hits:
                    per_bootloader[h["bootloader"]] += 1
        if args.write:
            path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")

    print(f"[INFO] {resolved:,} of {total:,} CVEs resolve to a corpus bootloader "
          f"({100 * resolved / total:.0f}%); {total - resolved:,} resolve to none")
    print(f"[INFO] strongest signal: " +
          ", ".join(f"{k} {v}" for k, v in per_signal.most_common()))
    print("[INFO] top bootloaders:")
    for name, count in per_bootloader.most_common(12):
        print(f"         {count:5d}  {name} ({names[name]})")
    if not args.write:
        print("[INFO] dry run; pass --write to store the field")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
