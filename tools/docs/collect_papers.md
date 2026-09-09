# `collect_papers.py`

Finds bootloader-related papers in the venues the SoK surveyed. Produces
[`PAPERS.md`](../../PAPERS.md).

The SoK examined the top four security venues and four software-engineering
venues for tools and techniques applicable to bootloaders, using
[top4grep](https://github.com/Kyle-Kyle/top4grep). This tool searches the same
source top4grep uses — dblp's SPARQL endpoint — with two differences:

* **All eight venues.** top4grep is hardcoded to the four security conferences,
  so the software-engineering half of the survey (where the general-purpose
  static-analysis and fuzzing tools come from) is out of its reach.
* **Standard library only.** top4grep needs `requests` and `sqlalchemy` and
  builds a local sqlite database first.

If you already have a top4grep database, `--from-top4grep` reads it instead of
querying the network, so a search can be reproduced from a fixed snapshot.

## Run it

```bash
python3 collect_papers.py --since 2015 --output papers.json --markdown ../PAPERS.md
```

About 10 seconds for ~17,500 papers across eight venues.

| Flag | Purpose |
|---|---|
| `--since YEAR` | Earliest publication year. Default 2015. |
| `--venue NAME` | Restrict to one venue. Repeatable, default all eight. |
| `--core-only` | Match only terms naming the boot chain, dropping broader firmware terms. |
| `--from-top4grep DB` | Read a top4grep sqlite database instead of querying dblp. |
| `--output FILE` | JSON output. Default `papers.json`. |
| `--markdown FILE` | Also write the grouped markdown index. |

Venues: IEEE S&P, ACM CCS, USENIX Security, NDSS, ICSE, FSE, ASE, OOPSLA.

## Two tiers

**Core** — the title names the boot chain (`bootloader`, `uefi`, `secure boot`,
`smm`, `bootkit`, `measured boot`, …). High precision: 16 matches, all genuinely
about boot.

**Context** — a broader firmware or embedded-systems term (`firmware`,
`microcontroller`, `rehosting`, `trustzone`, …). Noisier, but it is the
literature the SoK's tool survey draws on. `--core-only` drops it.

Every hit records which term matched, so the tier can be re-judged without
re-running the search.

## Contribution grouping

Each paper is assigned a contribution from its title by the ordered rules in
[`bootbench_keywords.py`](../bootbench_keywords.py) (`PAPER_CONTRIBUTIONS`),
first match wins: systematization → attack → discovery → rehosting → defense.
Rules rather than hand curation, so the index regenerates when the search does.

## Caveats

**Titles only.** dblp's SPARQL endpoint exposes titles, not abstracts, so a
paper that never names the boot chain in its title lands in the context tier or
is missed. The SoK's own reference list is the better source for those.

**`bootstrap` is deliberately not a keyword.** Every title it matched was FHE
bootstrapping or the machine-learning sense ("Bootstrap Conversational
Agents"), never the boot chain — the same failure mode as `dos` matching
"TODOs" in commit messages.

**OOPSLA coverage is partial.** OOPSLA moved to PACMPL, and `conf/oopsla` holds
only ~105 papers since 2015. dblp's REST API sits behind a bot check, so the
SPARQL endpoint is the only usable entry point.
