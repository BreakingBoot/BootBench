#!/usr/bin/env python3
"""Generate the BootBench wiki.

One page per bootloader and one per analysis tool. The structural content --
CVE counts, attack surfaces, defenses, commit history, verified runs -- comes
from the datasets, so a page cannot drift from the data it describes. The
explanation of what a bootloader does and why it is its type is curated in
`wiki_content.py`, because that judgement cannot be generated.

Usage
-----
    python3 generate_wiki.py --root .. --output ../wiki
"""

from __future__ import annotations

import argparse
import configparser
import glob
import re
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bootbench_keywords import ATTACK_SURFACES, TYPE_LABELS  # noqa: E402
from wiki_content import BOOTLOADERS, Bootloader, Stage  # noqa: E402

TYPES = ("type1", "type2", "type3")
SURFACE_LABEL = {s[0]: s[2] for s in ATTACK_SURFACES}
SURFACE_KIND = {s[0]: s[1] for s in ATTACK_SURFACES}

# The eight-stage model of SoK Figure 1. Stages 1-4 are the four Type 1 stages;
# EDK II's SEC/PEI/DXE/BDS map onto them directly (S 3.1), and stage 4 is named
# as the bootloader handoff in S 2.1.1. Stages 5-8 are the four Type 2 stages,
# enumerated in S 3.4 as the phases Windows Boot Manager runs through. A stage
# says what must happen, not how many components a project uses to do it.
BOOT_STAGES = (
    (1, "**Reset and early init.** Execution begins at the reset vector. Temporary "
        "memory is established, basic CPU state is set up, and the first integrity "
        "check establishes the root of trust. *EDK II SEC, coreboot bootblock, "
        "SeaBIOS preinit, U-Boot SoC ROM code.*",
        "Type 1, Type 3"),
    (2, "**Permanent memory.** CPU initialisation is completed and DRAM is brought "
        "up, so later stages have real memory to run in. *EDK II PEI, coreboot "
        "romstage, U-Boot SPL.*",
        "Type 1, Type 3"),
    (3, "**Device enumeration and drivers.** Buses are walked, devices matched to "
        "drivers, platform tables built, and the firmware's services published. "
        "*EDK II DXE, coreboot ramstage, SeaBIOS setup.*",
        "Type 1, Type 3"),
    (4, "**Bootloader handoff.** A boot device is selected and the OS bootloader is "
        "loaded and entered. *EDK II BDS, SeaBIOS INT 0x19, coreboot's payload jump.*",
        "Type 1 only — absent in Type 3, which has nothing to hand off to"),
    (5, "**Boot libraries.** The OS bootloader's own services: filesystem access, "
        "memory management, and whatever it needs to read its configuration. *GRUB "
        "kernel.img, Windows Boot Manager's boot libraries.*",
        "Type 2, Type 3"),
    (6, "**Boot configuration.** The description of what may be booted is read: "
        "entries, kernel arguments, and which extras to load. *grub.cfg, the Windows "
        "BCD, U-Boot's bootdev and environment.*",
        "Type 2, Type 3"),
    (7, "**Modules and boot drivers.** Extra code named by the configuration is "
        "loaded — filesystem, video, crypto or OS-specific drivers. *GRUB \\*.mod "
        "modules, Windows boot drivers.*",
        "Type 2, Type 3"),
    (8, "**OS handoff.** The kernel and initrd are loaded, the arguments and tables "
        "assembled, firmware resources released, and control transferred. *GRUB "
        "core.img, bootmgr.efi, U-Boot's bootflow.*",
        "Type 2, Type 3"),
)

# SoK S 2.3 -- the three ways state crosses a stage boundary.
COMMUNICATION_STYLES = (
    ("Structured handoff: system tables and interrupts",
     "Type 1 bootloaders publish an explicit interface. UEFI defines system tables "
     "exposing Boot Services and Runtime Services, with persistent configuration in "
     "NVRAM variables such as `BootOrder` and the Secure Boot keys; PEI reaches DXE "
     "through a HOB list. SeaBIOS, following legacy BIOS convention, uses software "
     "interrupts and fixed low-memory structures instead — `INT 0x19` to find the next "
     "stage, the BIOS Data Area for state. coreboot provides no user-facing interface "
     "at all: it builds a coreboot table and leaves the payload to define how anything "
     "is configured."),
    ("Dynamic configuration: external files",
     "Type 2 bootloaders move the contract into data. GRUB's `grub.cfg` holds menu "
     "entries, kernel arguments and chainload targets; the Windows BCD holds boot "
     "paths, recovery modes and drivers, editable at runtime. Because these are files "
     "rather than compiled-in values, the boot flow can change — a different root "
     "device, an alternate payload, a recovery entry — without rebuilding anything. "
     "That flexibility is also why the configuration file is itself an attack surface."),
    ("Static communication: minimal runtime interfaces",
     "Type 3 bootloaders fold initialisation and OS launch into one image and leave "
     "few channels open. MCUboot's only runtime channel is the flash layout — image "
     "slots and the trailer flags that record a pending, testing or confirmed update. "
     "U-Boot is the richer case, offering a shell and an environment that can adjust "
     "the bootflow or kernel arguments, but substantial change still means reflashing."),
)

# SoK S 2.4 -- the three handoff styles.
HANDOFF_STYLES = (
    ("Structured and layered",
     "Type 1 bootloaders use formal transitions. UEFI's BDS phase walks `BootOrder` to "
     "find a boot application, loads it with a pointer to the system table, and the "
     "application later calls `ExitBootServices()` to release firmware-managed "
     "resources. SeaBIOS chains through sector loaders: `INT 0x19` loads the MBR, whose "
     "code finds the active partition's volume boot record. coreboot delegates, handing "
     "its table to a payload that builds the real system tables itself."),
    ("Configurable OS handoff",
     "Type 2 bootloaders emphasise flexibility. `bootmgr.efi` passes UEFI tables, BCD "
     "entries and preloaded drivers to `winload.efi`; GRUB loads a kernel and initrd "
     "with a command line it assembled, or chainloads another Type 2 bootloader "
     "entirely. Multi-OS booting and runtime reconfiguration come from this stage."),
    ("Direct and minimal",
     "Type 3 bootloaders pass as little as possible. MCUboot verifies an image and "
     "jumps to it with nothing passed at all, since everything was fixed at build time. "
     "U-Boot passes more — kernel, arguments and a flattened device tree it may have "
     "fixed up — but the transfer is still essentially static. Determinism is chosen "
     "over extensibility."),
)


def slug(name: str) -> str:
    return name.replace("/", "-").replace(" ", "-")


# A GitHub wiki is a separate repository whose pages are addressed by filename.
# Subdirectories are not reliably navigable there, so --flat writes every page
# to the top level with a prefix instead.
FLAT = False


def page_path(out: Path, section: str, name: str) -> Path:
    if FLAT:
        return out / f"{section.capitalize()}-{slug(name)}.md"
    return out / section / f"{slug(name)}.md"


def page_link(section: str, name: str) -> str:
    if FLAT:
        return f"{section.capitalize()}-{slug(name)}"
    return f"{section}/{slug(name)}"


def load(root: Path) -> dict[str, Any]:
    parser = configparser.ConfigParser()
    parser.read_string((root / "oss-bootloaders" / ".gitmodules").read_text(encoding="utf-8"))
    corpus = {}
    for section in parser.sections():
        if not parser.has_option(section, "path"):
            continue
        path = parser.get(section, "path")
        btype, _, name = path.partition("/")
        corpus[name] = {"type": btype, "path": path,
                        "url": parser.get(section, "url", fallback="")}

    cves: dict[str, dict] = {}
    for btype in TYPES:
        p = root / "bootloader_cve_db" / btype / f"{btype}-results.json"
        if p.is_file():
            for cve_id, entry in json.loads(p.read_text(encoding="utf-8")).items():
                entry["_type"] = btype
                cves[cve_id] = entry

    commits: dict[str, dict] = {}
    for f in glob.glob(str(root / "bootloader_vuln_commits" / "type*" / "*.json")):
        name = Path(f).stem
        commits[name] = json.loads(Path(f).read_text(encoding="utf-8"))

    defenses = {}
    p = root / "oss-bootloaders" / "defenses.json"
    if p.is_file():
        defenses = json.loads(p.read_text(encoding="utf-8")).get("bootloaders", {})

    runners = json.loads((Path(__file__).resolve().parent /
                          "analysis_runners.json").read_text(encoding="utf-8"))
    tools = json.loads((Path(__file__).resolve().parent /
                        "analysis_tools.json").read_text(encoding="utf-8"))
    links = {}
    p = root / "bootloader_vuln_commits" / "cve-commit-links.json"
    if p.is_file():
        links = json.loads(p.read_text(encoding="utf-8"))

    return {"corpus": corpus, "cves": cves, "commits": commits,
            "defenses": defenses, "runners": runners, "tools": tools, "links": links}


def web_url(url: str) -> str:
    if url.startswith("git@"):
        host, _, repo = url[4:].partition(":")
        url = f"https://{host}/{repo}"
    return url.removesuffix(".git")


# The whole-boot figure: the eight stages, and which types cover which of them.
STAGE_MODEL_FIGURE = """```mermaid
%%{init: {"flowchart": {"htmlLabels": true}}}%%
flowchart LR
    HW(["Hardware<br/>power-on / reset"]):::edge --> S1
    subgraph T1["Type 1 &mdash; firmware bootloader"]
        direction LR
        S1["<b>1</b><br/>Reset and<br/>early init"]:::fw --> S2["<b>2</b><br/>Permanent<br/>memory"]:::fw
        S2 --> S3["<b>3</b><br/>Devices<br/>and drivers"]:::fw
        S3 --> S4["<b>4</b><br/>Bootloader<br/>handoff"]:::fw
    end
    S4 --> S5
    subgraph T2["Type 2 &mdash; OS bootloader"]
        direction LR
        S5["<b>5</b><br/>Boot<br/>libraries"]:::os --> S6["<b>6</b><br/>Boot<br/>configuration"]:::os
        S6 --> S7["<b>7</b><br/>Modules and<br/>boot drivers"]:::os
        S7 --> S8["<b>8</b><br/>OS<br/>handoff"]:::os
    end
    S8 --> OS(["Operating system<br/>or hypervisor"]):::edge
    classDef fw fill:#eef3fb,stroke:#4a6fa5;
    classDef os fill:#f3f0fb,stroke:#7a5aa5;
    classDef edge fill:#f6f6f6,stroke:#888,stroke-dasharray:3 3;
```"""

MONOLITHIC_FIGURE = """```mermaid
%%{init: {"flowchart": {"htmlLabels": true}}}%%
flowchart LR
    HW(["Hardware<br/>power-on / reset"]):::edge --> M1
    subgraph T3["Type 3 &mdash; monolithic bootloader"]
        direction LR
        M1["<b>1</b><br/>Reset and<br/>early init"]:::mono --> M2["<b>2</b><br/>Permanent<br/>memory"]:::mono
        M2 --> M3["<b>3</b><br/>Devices<br/>and drivers"]:::mono
        M3 -. "no stage 4:<br/>nothing to hand off to" .-> M5["<b>5-7</b><br/>Libraries, config<br/>and drivers"]:::mono
        M5 --> M8["<b>8</b><br/>OS<br/>handoff"]:::mono
    end
    M8 --> OS(["Operating system"]):::edge
    classDef mono fill:#eefbf3,stroke:#4a8f6a;
    classDef edge fill:#f6f6f6,stroke:#888,stroke-dasharray:3 3;
```"""

TYPES_FIGURE = """```mermaid
%%{init: {"flowchart": {"htmlLabels": true}}}%%
flowchart TB
    subgraph MONO["Monolithic boot"]
        direction TB
        B_OS["Operating system"]:::os
        B_T3["<b>Type 3</b><br/>Monolithic bootloader<br/><i>U-Boot, MCUboot, barebox</i>"]:::t3
        B_HW["Hardware"]:::hw
        B_HW --> B_T3 --> B_OS
    end
    subgraph SPLIT["Staged boot"]
        direction TB
        A_OS["Operating system<br/>or hypervisor"]:::os
        A_T2["<b>Type 2</b><br/>OS bootloader<br/><i>GRUB, shim, systemd-boot</i>"]:::t2
        A_T1["<b>Type 1</b><br/>Firmware bootloader<br/><i>EDK II, coreboot, SeaBIOS</i>"]:::t1
        A_HW["Hardware"]:::hw
        A_HW --> A_T1 --> A_T2 --> A_OS
    end
    classDef hw fill:#ececec,stroke:#666;
    classDef t1 fill:#eef3fb,stroke:#4a6fa5;
    classDef t2 fill:#f3f0fb,stroke:#7a5aa5;
    classDef t3 fill:#eefbf3,stroke:#4a8f6a;
    classDef os fill:#fdf3e7,stroke:#b07a3a;
```"""


MERMAID_THEME = """%%{init: {"flowchart": {"htmlLabels": true, "curve": "linear"}}}%%"""


def mm(text: str) -> str:
    """Make text safe inside a quoted Mermaid label."""
    return text.replace('"', "'").replace("|", "/")


# Where a bootloader's control comes from, which is what its type turns on.
ENTRY_LABEL = {
    "type1": "Hardware<br/>power-on / reset",
    "type2": "Firmware<br/>(a Type 1 bootloader)",
    "type3": "Hardware<br/>power-on / reset",
}


def flow_diagram(prose: Bootloader, btype: str) -> list[str]:
    """A figure of the boot flow: stages as nodes, what crosses as edge labels."""
    if not prose.stages:
        return []
    entry = ENTRY_LABEL.get(btype, "Entry")
    lines = ["```mermaid", MERMAID_THEME, "flowchart TD",
             f'    ENTRY(["{mm(entry)}"]):::edge']
    for i, stage in enumerate(prose.stages):
        lines.append(f'    S{i}["<b>{mm(stage.name)}</b>"]:::stage')
    lines.append(f'    TARGET(["{mm(prose.target)}"]):::edge')
    lines.append("    ENTRY --> S0")
    for i, stage in enumerate(prose.stages):
        nxt = f"S{i + 1}" if i + 1 < len(prose.stages) else "TARGET"
        lines.append(f'    S{i} -->|"{mm(stage.carries)}"| {nxt}')
    lines += ["    classDef stage fill:#eef3fb,stroke:#4a6fa5,stroke-width:1px;",
              "    classDef edge fill:#f6f6f6,stroke:#888,stroke-dasharray:3 3;",
              "```"]
    return lines


def resolve_links(text: str) -> str:
    """Rewrite `bootloader:name` targets in curated prose for the current layout."""
    return re.sub(r"\]\(bootloader:([^)]+)\)",
                  lambda m: f"]({page_link('bootloaders', m.group(1))})", text)


def boot_flow_section(prose: Bootloader, btype: str) -> list[str]:
    """The stage walkthrough, following the SoK case-study structure."""
    if not prose.stages:
        return []
    lines = ["## How it boots", ""]
    if prose.case_study:
        lines += [f"The SoK paper gives a full case study of this bootloader in "
                  f"section {prose.case_study}. See [Boot-Stages](Boot-Stages) for the "
                  f"eight-stage model these phases map onto.", ""]
    else:
        lines += ["See [Boot-Stages](Boot-Stages) for the eight-stage model these "
                  "phases map onto.", ""]
    lines += flow_diagram(prose, btype) + [""]
    for i, stage in enumerate(prose.stages, 1):
        lines.append(f"{i}. **{stage.name}** -- {stage.what}")
    lines += ["", "### Passing data between stages", "",
              resolve_links(prose.communication), ""]
    lines += ["### Handoff", "", resolve_links(prose.handoff), ""]
    return lines


def bootloader_page(name: str, data: dict[str, Any]) -> str:
    meta = data["corpus"][name]
    btype = meta["type"]
    prose = BOOTLOADERS.get(name, Bootloader(
        summary="", boot_role="Not yet described.", type_rationale="Not yet explained."))
    summary, role, rationale = prose.summary, prose.boot_role, prose.type_rationale

    mine = [c for c in data["cves"].values()
            if any(h["bootloader"] == name for h in c.get("bootloaders") or [])]
    surfaces: Counter = Counter()
    cwes: Counter = Counter()
    for c in mine:
        for h in c.get("attack_surfaces") or []:
            surfaces[h["surface"]] += 1
        for w in c.get("cwe_ids") or []:
            cwes[w] += 1

    commits = data["commits"].get(name, {})
    n_cve_commits = len(commits.get("CVEs", []))
    n_kw_commits = len(commits.get("vulnerability", []))
    defense = data["defenses"].get(name, {})
    features = sorted(defense.get("features", {}))

    linked = [(cid, f) for cid, e in data.get("links", {}).get("links", {}).items()
              for f in e["fixes"] if f["repo"].endswith("/" + name)]

    lines = [f"# {name}", "",
             f"*{summary}*" if summary else "",
             "",
             f"| | |", "|---|---|",
             f"| Type | **{TYPE_LABELS.get(btype, btype)}** ({btype}) |",
             f"| Upstream | {web_url(meta['url'])} |",
             f"| CVEs attributed | {len(mine)} |",
             f"| Vulnerability-fixing commits | {n_cve_commits} naming a CVE, {n_kw_commits} keyword-matched |",
             f"| CVEs with a linked fix | {len(linked)} |",
             "",
             "## What it does at boot", "", role, "",
             f"## Why it is {btype.replace('type', 'Type ')}", "", rationale, "",
             ]

    lines += boot_flow_section(prose, btype)

    if surfaces:
        lines += ["## Attack surfaces seen in its CVEs", "",
                  "| Surface | | CVEs |", "|---|---|---:|"]
        for sid, count in surfaces.most_common():
            lines.append(f"| `{sid}` | {SURFACE_LABEL[sid]} ({SURFACE_KIND[sid]}) | {count} |")
        lines.append("")

    if cwes:
        lines += ["## Most common weaknesses", "", "| CWE | CVEs |", "|---|---:|"]
        for cwe, count in cwes.most_common(8):
            lines.append(f"| {cwe} | {count} |")
        lines.append("")

    lines += ["## Security mechanisms", ""]
    if features:
        lines += ["Detected in its build configuration and source:", ""]
        lines += [f"- {f.replace('_', ' ')}" for f in features]
        lines += ["", "See [Security-Mechanisms](Security-Mechanisms) for how these are detected "
                  "and what a detection does and does not prove.", ""]
    else:
        lines += ["None detected. That means no matching pattern was found in its build "
                  "configuration or source, not that the project is insecure -- a small MCU "
                  "bootloader may simply have nothing to configure.", ""]

    if linked:
        lines += ["## Reproducible vulnerabilities", "",
                  "Each of these resolves to a fixing commit and to the parent revision that "
                  "still contains the bug:", "",
                  "| CVE | Fix | Vulnerable revision |", "|---|---|---|"]
        for cid, fix in sorted(linked, key=lambda x: x[0])[:15]:
            lines.append(f"| {cid} | `{fix['commit'][:10]}` | `{fix['parent'][:10]}` |")
        if len(linked) > 15:
            lines.append(f"| … and {len(linked) - 15} more | | |")
        lines += ["", "```bash",
                  f"git -C oss-bootloaders/{meta['path']} checkout <vulnerable revision>",
                  "```", ""]

    lines += ["## Analysing it", "",
              "```bash",
              f"git -C oss-bootloaders submodule update --init {meta['path']}",
              f"./scripts/analysis/run-tool.sh codeql {name}",
              "```", "",
              "See [Tools](Tools) for what each tool applies to.", "",
              "---", "", "[Home](Home) · "
              f"[{TYPE_LABELS.get(btype, btype)}](Bootloader-Types) · [Tools](Tools)", ""]
    return "\n".join(l for l in lines if l is not None)


def tool_page(tool: dict[str, Any], runner: dict[str, Any], root: Path) -> str:
    name = tool["name"]
    status = runner.get("status", "unknown")
    lines = [f"# {name}", "", f"*{tool.get('why') or tool.get('description', '')}*", "",
             "| | |", "|---|---|",
             f"| Category | {tool.get('category_label', '—')} |",
             f"| Consumes | {runner.get('input', '—')} |",
             f"| Status | `{status}` |",
             f"| Upstream | {tool.get('url', '—')} |",
             f"| Language | {tool.get('language') or '—'} |",
             "", "## What it does", "", runner.get("summary", ""), "",
             "## What it applies to", "", runner.get("applies_to", ""), ""]

    if runner.get("verified_on"):
        target, _, result = runner["verified_on"].partition(" -> ")
        lines += ["## Verified run", "",
                  f"Run against **{target}**: {result}", ""]

    if runner.get("runner"):
        lines += ["## Walkthrough", "", "```bash",
                  "# what this tool can be pointed at",
                  "./scripts/analysis/run-tool.sh --list", "",
                  f"# run it",
                  f"./scripts/analysis/run-tool.sh {name} <target>", "",
                  "# results",
                  f"ls analysis-results/{name}/", "```", "",
                  "The first run builds a container image, which can take a while. Everything "
                  "afterwards reuses it. Output ownership is handed back to you on exit, "
                  "including when a run fails.", ""]
    else:
        lines += ["## Running it", "",
                  "No runner is provided. " + (runner.get("blocker") or ""), ""]

    if runner.get("notes"):
        lines += ["## Notes", "", runner["notes"], ""]

    if runner.get("blocker") and runner.get("runner"):
        lines += ["## Limits", "", runner["blocker"], ""]

    lines += ["---", "", "[Home](Home) · [Tools](Tools) · "
              "[Patches](https://github.com/BreakingBoot/BootBench/blob/main/scripts/analysis/PATCHES.md)", ""]
    return "\n".join(lines)


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=here.parent)
    parser.add_argument("--output", type=Path, default=here.parent / "wiki")
    parser.add_argument("--flat", action="store_true",
                        help="write every page at the top level, for a GitHub wiki")
    args = parser.parse_args()

    global FLAT
    FLAT = args.flat

    root = args.root.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not FLAT:
        (out / "bootloaders").mkdir(parents=True, exist_ok=True)
        (out / "tools").mkdir(parents=True, exist_ok=True)
    data = load(root)

    for name in sorted(data["corpus"]):
        page_path(out, "bootloaders", name).write_text(
            bootloader_page(name, data), encoding="utf-8")
    runners = {r["name"]: r for r in data["runners"]}
    for tool in data["tools"]:
        runner = runners.get(tool["name"], {})
        page_path(out, "tools", tool["name"]).write_text(
            tool_page(tool, runner, root), encoding="utf-8")

    write_indexes(out, data)
    print(f"[INFO] {len(data['corpus'])} bootloader pages, {len(data['tools'])} tool pages")
    print(f"[INFO] wiki written to {out}")
    return 0


def write_indexes(out: Path, data: dict[str, Any]) -> None:
    corpus = data["corpus"]
    by_type: dict[str, list[str]] = defaultdict(list)
    for name, meta in corpus.items():
        by_type[meta["type"]].append(name)

    # Home
    lines = ["# BootBench wiki", "",
             "Reference pages for the bootloader corpus and the analysis tools.", "",
             "## Start here", "",
             "- **[Bootloader-Types](Bootloader-Types)** — what Type 1, 2 and 3 mean and how "
             "a bootloader is placed",
             "- **[Boot-Stages](Boot-Stages)** — the eight stages of a boot, how state crosses between them, and the three handoff styles",
             "- **[Attack-Surfaces](Attack-Surfaces)** — the six surfaces and how entries are mapped onto them",
             "- **[Security-Mechanisms](Security-Mechanisms)** — what the corpus defends itself with",
             "- **[Bootloaders](Bootloaders)** — a page per bootloader",
             "- **[Tools](Tools)** — a page per analysis tool, with walkthroughs",
             "", "## The corpus at a glance", "",
             "| Type | | Bootloaders |", "|---|---|---:|"]
    for btype in TYPES:
        lines.append(f"| `{btype}` | {TYPE_LABELS[btype]} | {len(by_type[btype])} |")
    runnable = sum(1 for r in data["runners"] if r["status"] == "runnable")
    lines += ["", f"{len(data['cves']):,} CVEs · "
              f"{sum(len(c.get('CVEs', [])) + len(c.get('vulnerability', [])) for c in data['commits'].values()):,} "
              f"vulnerability-fixing commits · {runnable} of {len(data['runners'])} analysis tools runnable", ""]
    (out / "Home.md").write_text("\n".join(lines), encoding="utf-8")

    # Bootloaders index
    lines = ["# Bootloaders", "",
             "Every project in the corpus, grouped by type. Each page explains what the "
             "bootloader does at boot, the stages it runs through and how each stage "
             "passes state to the next, why it is classified as it is, the attack "
             "surfaces its CVEs touch, and what it defends itself with.", ""]
    for btype in TYPES:
        lines += [f"## {TYPE_LABELS[btype]} (`{btype}`)", "",
                  "| Bootloader | What it is |", "|---|---|"]
        for name in sorted(by_type[btype]):
            summary = getattr(BOOTLOADERS.get(name), "summary", "")
            lines.append(f"| [{name}]({page_link('bootloaders', name)}) | {summary} |")
        lines.append("")
    (out / "Bootloaders.md").write_text("\n".join(lines), encoding="utf-8")

    # Tools index
    runners = {r["name"]: r for r in data["runners"]}
    lines = ["# Tools", "",
             "The analysis tools BootBench collects, with a page each covering how the tool "
             "works, what it applies to, and a walkthrough.", "",
             "| Tool | Applies to | Status |", "|---|---|---|"]
    for tool in sorted(data["tools"], key=lambda t: t["name"].lower()):
        r = runners.get(tool["name"], {})
        lines.append(f"| [{tool['name']}]({page_link('tools', tool['name'])}) | "
                     f"{r.get('applies_to', '—')[:90]} | `{r.get('status', '—')}` |")
    lines.append("")
    (out / "Tools.md").write_text("\n".join(lines), encoding="utf-8")

    # Types
    lines = ["# Bootloader types", "",
             "BootBench classifies every bootloader by **where it starts** and **what it "
             "hands off to**. That is the whole test, and it is why two projects that look "
             "similar can land in different types.", "", TYPES_FIGURE, ""]
    detail = {
        "type1": ("Boots from hardware and presents a hardware-agnostic interface to whatever "
                  "runs next. It may load another bootloader or a standalone application, but "
                  "it does not itself prepare an operating system.",
                  "Starts at the reset vector with nothing initialised. Ends by publishing an "
                  "interface — UEFI Boot Services, the BIOS interrupt table, the RISC-V SBI — "
                  "and handing off."),
        "type2": ("Boots from an already-initialised system and prepares an operating system "
                  "or hypervisor.",
                  "Starts with the machine already up. Its job is to find a kernel, load it, "
                  "and transfer control with the right arguments and tables. This is why Type 2 "
                  "bootloaders are configuration-driven and often scriptable."),
        "type3": ("Combines both jobs: boots directly from hardware into an operating system "
                  "with no handoff between stages.",
                  "Starts at reset and ends in the application or kernel. Nothing sits between, "
                  "so the interfaces a staged boot exposes between stages simply do not exist."),
    }
    for btype in TYPES:
        summary, test = detail[btype]
        lines += [f"## {TYPE_LABELS[btype]} (`{btype}`)", "", summary, "",
                  f"**The test:** {test}", "",
                  f"{len(by_type[btype])} in the corpus: " +
                  ", ".join(f"[{n}]({page_link('bootloaders', n)})" for n in sorted(by_type[btype])), ""]
    lines += ["## Staged versus monolithic booting", "",
              "Type 1 and Type 2 chained together are *staged booting* — modular and "
              "hardware-abstracting, at the cost of firmware size and start-up time, and "
              "typical of desktops, servers and phones. Type 3 is *monolithic booting* — "
              "smaller and faster but tightly coupled to the board, and typical of IoT devices "
              "and microcontrollers.", "",
              "## Where the classification is arguable", "",
              "A few projects genuinely straddle the line, and their pages say so rather than "
              "presenting the placement as settled:", "",
              "- **arm-trusted-firmware** spans reset to OS handoff, so it is Type 3 here — but "
              "in a staged setup where BL33 is U-Boot it behaves as Type 1.",
              "- **lk** is Type 2 as Qualcomm's aboot, running after the SoC's primary "
              "bootloader; on platforms where it is the only stage it is Type 3.",
              "- **open-iscsi** is boot-path infrastructure rather than a bootloader that "
              "transfers control to a kernel. It is the weakest fit in the corpus.", ""]
    (out / "Bootloader-Types.md").write_text("\n".join(lines), encoding="utf-8")

    # Boot stages
    documented = {n: BOOTLOADERS[n] for n in sorted(corpus) if n in BOOTLOADERS
                  and BOOTLOADERS[n].stages}
    lines = ["# Boot stages", "",
             "A boot is a sequence of stages, each setting up what the next one needs. The SoK "
             "divides it into eight, and every bootloader page walks its own phases against "
             "this model. Not every stage appears everywhere: Type 3 has no stage 4, because "
             "there is no second bootloader to hand off to, and Type 1 has no stages 5-8, "
             "because it stays OS-agnostic.", "",
             STAGE_MODEL_FIGURE, "",
             "A Type 3 bootloader spans the same work in one image, with no stage 4 "
             "because there is no second bootloader to hand off to:", "",
             MONOLITHIC_FIGURE, "",
             "| Stage | | Present in |", "|---|---|---|"]
    for num, what, present in BOOT_STAGES:
        lines.append(f"| {num} | {what} | {present} |")
    lines += ["", "Implementations vary widely inside a stage. coreboot spreads stage 3 across "
              "several components (romstage, postcar, ramstage); EDK II packs the same work "
              "into one (DXE). The stage numbers describe *what must happen*, not how a "
              "project divides it up.", "",
              "## How state crosses a stage boundary", ""]
    for title, body in COMMUNICATION_STYLES:
        lines += [f"### {title}", "", body, ""]
    lines += ["## How control crosses it", ""]
    for title, body in HANDOFF_STYLES:
        lines += [f"### {title}", "", body, ""]
    lines += ["## Per-bootloader walkthroughs", "",
              "Every corpus page carries a **How it boots** section with its own phases, the "
              "mechanism that carries state between them, and what it hands over. Six of the "
              "paper's seven case studies are in the corpus:", ""]
    for name, prose in documented.items():
        if prose.case_study:
            lines.append(f"- [{name}]({page_link('bootloaders', name)}) — SoK § {prose.case_study}")
    n_cited = sum(1 for p in documented.values() if p.case_study)
    lines += ["", "The seventh, Windows Boot Manager, is closed source and so is not in the "
              "corpus; its structure is described under stages 5-8 above and in SoK § 3.4.", "",
              f"The remaining {len(documented) - n_cited} pages are written from each "
              "project's own documentation and source.", ""]
    (out / "Boot-Stages.md").write_text("\n".join(lines), encoding="utf-8")

    # Attack surfaces
    surfaces: Counter = Counter()
    per_type: dict[str, Counter] = {t: Counter() for t in TYPES}
    for entry in data["cves"].values():
        hits = entry.get("attack_surfaces") or []
        if hits:
            surfaces[hits[0]["surface"]] += 1
            per_type[entry["_type"]][hits[0]["surface"]] += 1
    lines = ["# Attack surfaces", "",
             "The six surfaces the SoK defines, and how the dataset maps onto them. Every CVE "
             "and every mined commit carries an `attack_surfaces` field listing the surfaces "
             "its text touches, with the matched wording recorded so a classification can be "
             "checked.", "",
             "| | Kind | Surface | Reached through |", "|---|---|---|---|"]
    reached = {
        "SAS3": "SMM, SMI handlers, UEFI Runtime Services — code still live after the OS starts",
        "SAS1": "PXE, TFTP, DHCP, HTTP boot, iSCSI — anything the bootloader fetches over a network",
        "SAS4": "Boot menus, GRUB and UEFI shells, recovery and download modes",
        "SAS2": "Variables, configuration files, partition tables, filesystems, boot logos, ACPI tables",
        "HAS2": "USB, DMA, PCIe, removable media — a device an attacker can attach",
        "HAS1": "SPI flash, JTAG, glitching — an attacker who opens the case",
    }
    for sid, kind, label, _ in ATTACK_SURFACES:
        lines.append(f"| `{sid}` | {kind} | {label} | {reached[sid]} |")
    lines += ["", "## What the data shows", "",
              "Primary surface per CVE, by bootloader type. The primary is the "
              "highest-precedence surface present, not a judgement about which mattered most.", "",
              "| Type | " + " | ".join(f"`{s[0]}`" for s in ATTACK_SURFACES) + " |",
              "|---|" + "---|" * len(ATTACK_SURFACES)]
    for btype in TYPES:
        row = " | ".join(str(per_type[btype].get(s[0], 0)) for s in ATTACK_SURFACES)
        lines.append(f"| {TYPE_LABELS[btype]} | {row} |")
    lines += ["", "The shape matches the taxonomy. Type 1 is dominated by post-boot features — "
              "SMM and runtime services are what a firmware bootloader leaves running. Type 2 "
              "spreads across persistent data sources, remote access and boot-time features, "
              "which is what a configuration-driven, network-capable OS loader exposes. Type 3 "
              "concentrates in persistent data sources, because a monolithic bootloader's "
              "attack surface is mostly the images and data it parses.", "",
              "## Limits", "",
              "Mapping is done on the text of a CVE description or commit message, so it "
              "inherits their vagueness. Around a third of CVEs and a sixth of commits map to "
              "any surface at all; the rest simply do not say enough. A description that "
              "mentions PXE in passing will be counted as remote access even if the flaw is in "
              "configuration parsing — BootHole is exactly that case.", ""]
    (out / "Attack-Surfaces.md").write_text("\n".join(lines), encoding="utf-8")

    # Security mechanisms
    coverage: Counter = Counter()
    for entry in data["defenses"].values():
        for feature in entry.get("features", {}):
            coverage[feature] += 1
    total = len(data["defenses"]) or 1
    lines = ["# Security mechanisms", "",
             "What the corpus defends itself with, scanned from build configuration and "
             "source.", "",
             "| Mechanism | Bootloaders |", "|---|---:|"]
    for feature, count in coverage.most_common():
        lines.append(f"| {feature.replace('_', ' ')} | {count} of {total} |")
    lines += ["", "## Reading this honestly", "",
              "A detection means a pattern matched build configuration or source. That is "
              "evidence the project *has* the feature — not that a given build enables it, and "
              "not that the implementation is correct. Every detection stores the file and the "
              "matched text so a claim can be checked.", "",
              "Two patterns were deliberately narrowed after inspecting what they matched. "
              "`CFI` is not matched bare: in bootloaders it overwhelmingly means *Common Flash "
              "Interface*, and bare matching credited u-boot's MIPS Kconfig and wolfBoot's NXP "
              "flash HAL with control-flow integrity. `TPM` is anchored to symbol forms rather "
              "than the bare acronym.", "",
              "## Declared versus enabled", "",
              "Declared features are a property of the project. Binary mitigations — NX, RELRO, "
              "PIE, stack protector, FORTIFY — are a property of one build, read from an "
              "artifact with `readelf` and `nm`. A bootloader can implement Secure Boot and "
              "still compile without a stack protector, so the two are never merged.", ""]
    (out / "Security-Mechanisms.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
