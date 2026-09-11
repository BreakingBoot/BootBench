# `generate_wiki.py`

Generates [`wiki/`](../../wiki/): a page per bootloader and a page per analysis
tool.

```bash
python3 generate_wiki.py --root .. --output ../wiki          # for the repo
python3 generate_wiki.py --root .. --output /tmp/w --flat    # for a GitHub wiki
```

`--flat` writes every page at the top level with a prefix
(`Bootloaders-u-boot.md`) and rewrites links to match, because a GitHub wiki
addresses pages by filename. `scripts/publish-wiki.sh` uses it.

## Split between generated and curated

**Generated from the datasets:** CVE counts, attributed CWEs, attack surfaces,
detected security mechanisms, commit history, linked reproducible
vulnerabilities, tool status and verified runs. A page cannot drift from the
data it describes, and regenerating after a refresh updates every page.

**Curated in [`wiki_content.py`](../wiki_content.py):** what a bootloader
actually does at boot, the stages it runs through, how each stage passes state
to the next, what it hands over at the end, and why that places it in Type 1, 2
or 3. That judgement cannot be generated — it is the part a reader most needs
and the part a script cannot infer.

Each entry is a `Bootloader` dataclass:

| Field | What it holds |
|---|---|
| `summary` | One line, used on index pages |
| `boot_role` | What it does at boot |
| `type_rationale` | Why it is Type 1, 2 or 3 |
| `stages` | Ordered `Stage` records: `name`, `what` it does, and what it `carries` to the next stage |
| `target` | What the last stage hands control to — the right-hand chip in the figure |
| `communication` | How state reaches the next stage |
| `handoff` | What is passed at the final boundary, and to whom |
| `case_study` | SoK section, for the six the paper details |

`stages`, `communication` and `handoff` follow the structure the SoK uses for
its case studies (§ 3). Each stage's `carries` field labels the arrow leaving
it in the generated figure, so it should name the artifact that crosses the
boundary — a HOB list, a device tree, a filled-in struct — rather than repeating
what the stage did. Prose may link to another bootloader by writing the target as
`bootloader:<name>`; the generator rewrites it for whichever layout it is
rendering, so prose never hardcodes nested or flat links.

Tests fail if a corpus bootloader has no prose, if prose exists for a bootloader
no longer in the corpus, if any stage walkthrough is blank, if a `case_study` is
claimed for a bootloader the paper does not detail, or if any internal link in
either layout does not resolve.

## Figures

Every bootloader page carries a **boot timeline**: stages left to right, an
axis beneath them with an arrow per transition, and the label under each
segment naming what crosses that boundary. The chip on the left says where
control comes from — hardware reset for Type 1 and 3, firmware for Type 2 — and
the chip on the right is what it hands to. Each type has its own accent colour.

These are SVG, written to `wiki/figures/<name>.svg` by
[`boot_figure.py`](../boot_figure.py), because Mermaid lays diagrams out
automatically and cannot put an axis under a row of stages. Column widths are
driven by the text, so a figure is as wide as it needs to be and no wider;
median is about 1000px, which GitHub shows near full size.

Two projects get no figure: `lbmk` is a build system and `edk2-platforms` is a
set of packages, so drawing either as reset → stage → OS would assert a boot
sequence they do not have. `has_real_flow()` detects the placeholder stage.

The three overview diagrams on `Boot-Stages` and `Bootloader-Types` remain
Mermaid, since they group things into bands rather than showing a timeline.

[`scripts/check-diagrams.sh`](../../scripts/check-diagrams.sh) checks both: the
SVGs for well-formed XML, a figure per page that claims one, and orphans; the
Mermaid blocks through the real renderer. The test suite additionally checks
that every stage and ordinal reaches the figure and that stage names do not
wrap out of their boxes.

## Pages

| Page | Contents |
|---|---|
| `Home` | Index and corpus summary |
| `Bootloader-Types` | What Type 1/2/3 mean, the test used, and where classification is arguable |
| `Boot-Stages` | The eight-stage model with figures, the three ways state crosses a boundary, and the three handoff styles |
| `Attack-Surfaces` | The six surfaces, what reaches each, and the observed distribution |
| `Security-Mechanisms` | What the corpus defends itself with, and how to read a detection |
| `Bootloaders` | Index of all 62, grouped by type |
| `bootloaders/<name>` | One per bootloader |
| `Tools` | Index of all 24 analysis tools |
| `tools/<name>` | One per tool, with a walkthrough |

## Adding a bootloader

Add it to `oss-bootloaders` with `scripts/add-bootloaders.sh`, write its entry
in `wiki_content.py`, and regenerate. Two fields carry most of the weight:
`type_rationale`, which should answer where the bootloader starts and what it
hands off to, because that is what the taxonomy turns on; and `stages` with its
`communication` and `handoff`, which is what a reader needs in order to follow
what actually happens at each boundary. Give every stage a `carries` and the
bootloader a `target`, or the figure cannot be drawn and a test will say so.
