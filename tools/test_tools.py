#!/usr/bin/env python3
"""Test suite for the BootBench tools.

Hermetic: the git-dependent tests build throwaway repositories with known
history in a temp directory, so they need no network and no submodule checkout.
Tests that compare against the published dataset skip themselves if the data
submodules are not initialised.

    python3 test_tools.py            # run everything
    python3 test_tools.py -v         # per-test detail
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DB = ROOT / "bootloader_cve_db"
sys.path.insert(0, str(HERE))

import bootbench_keywords as kw  # noqa: E402
import classify_cves  # noqa: E402
import collect_papers  # noqa: E402
import cve_stats  # noqa: E402
import extract_vuln_commits as miner  # noqa: E402

TYPES = ("type1", "type2", "type3")
HAS_CVE_DB = all((DB / t / f"{t}-results.json").is_file() for t in TYPES)


def run_tool(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HERE / script), *args],
                          capture_output=True, text=True)


def git(repo: Path, *args: str, **env_extra: str) -> str:
    env = {**os.environ,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           **env_extra}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, check=True, env=env).stdout.strip()


def make_repo(path: Path, commits: list[str]) -> list[str]:
    """Create a linear repo whose commit messages are ``commits``, oldest first."""
    path.mkdir(parents=True, exist_ok=True)
    git(path.parent, "init", "-q", "-b", "main", path.name)
    hashes = []
    for i, message in enumerate(commits):
        (path / "f.txt").write_text(str(i))
        git(path, "add", "f.txt")
        git(path, "commit", "-q", "-m", message,
            GIT_AUTHOR_DATE=f"2020-01-{i + 1:02d}T00:00:00+0000",
            GIT_COMMITTER_DATE=f"2020-01-{i + 1:02d}T00:00:00+0000")
        hashes.append(git(path, "rev-parse", "HEAD"))
    return hashes


# ---------------------------------------------------------------------------
# Classification rules
# ---------------------------------------------------------------------------

@unittest.skipUnless(HAS_CVE_DB, "bootloader_cve_db not initialised")
class TestClassificationFidelity(unittest.TestCase):
    """The rules must reproduce the published dataset, or they are not the rules."""

    def test_keyword_breakdown_reproduced_exactly(self):
        for name in TYPES:
            with self.subTest(type=name):
                results = json.loads((DB / name / f"{name}-results.json").read_text())
                published = json.loads((DB / name / f"{name}-keyword-breakdown.json").read_text())
                include = kw.compile_keywords(kw.BOOTLOADER_TYPES[name][0])
                replayed: dict[str, int] = {}
                for entry in results.values():
                    hit = kw.first_match(entry["description"], include)
                    self.assertIsNotNone(hit, f"{entry['cve_id']} matches no include keyword")
                    replayed[hit] = replayed.get(hit, 0) + 1
                self.assertEqual(replayed, published)

    def test_exclude_lists_reject_none_of_their_own(self):
        for name in TYPES:
            with self.subTest(type=name):
                results = json.loads((DB / name / f"{name}-results.json").read_text())
                exclude = kw.compile_keywords(kw.BOOTLOADER_TYPES[name][1])
                rejected = [c for c, e in results.items()
                            if kw.first_match(e["description"], exclude) is not None]
                self.assertEqual(rejected, [])

    def test_type3_exclude_covers_type1_vocabulary(self):
        missing = set(kw.TYPE1_INCLUDE) - set(kw.TYPE3_EXCLUDE)
        self.assertEqual(missing, set())

    def test_first_match_is_order_sensitive(self):
        pats = kw.compile_keywords(["uefi", "bios"])
        self.assertEqual(kw.first_match("a UEFI BIOS bug", pats), "uefi")
        self.assertEqual(kw.first_match("a UEFI BIOS bug",
                                        kw.compile_keywords(["bios", "uefi"])), "bios")

    def test_classification_is_not_plural_tolerant(self):
        # Plural tolerance is for commit messages only.  Enabling it here would
        # change the published keyword breakdown.
        pats = kw.compile_keywords(["bios"])
        self.assertIsNone(kw.first_match("two bioses on the board", pats))
        plural = kw.compile_keywords(["bios"], allow_plural=True)
        self.assertIsNotNone(kw.first_match("two bioses on the board", plural))

    def test_matching_is_word_bounded(self):
        pats = kw.compile_keywords(["boot services"])
        self.assertIsNone(kw.first_match("reboot servicesX", pats))
        self.assertIsNotNone(kw.first_match("uses Boot Services here", pats))


class TestClassifyCvesEndToEnd(unittest.TestCase):
    """Run the actual script over a corpus laid out like cvelistV5."""

    @staticmethod
    def record(cve_id: str, description: str, state: str = "PUBLISHED") -> dict:
        cna: dict = {"providerMetadata": {"shortName": "test"}}
        if state == "REJECTED":
            cna["rejectedReasons"] = [{"lang": "en", "value": "DO NOT USE"}]
        else:
            cna["descriptions"] = [{"lang": "en", "value": description}]
            cna["affected"] = [{"vendor": "ExampleCorp", "product": "p"}]
            cna["problemTypes"] = [{"descriptions": [{"description": "CWE-787: Out-of-bounds Write",
                                                      "lang": "en", "type": "text"}]}]
        return {"dataType": "CVE_RECORD", "dataVersion": "5.0", "containers": {"cna": cna},
                "cveMetadata": {"cveId": cve_id, "state": state,
                                "datePublished": "2020-01-01T00:00:00"}}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.corpus = Path(self.tmp.name) / "cvelistV5"
        (self.corpus / "cves" / "2020" / "1xxx").mkdir(parents=True)
        self.write("CVE-2020-1001", "A SMM handler flaw in the system firmware.")
        self.write("CVE-2020-1002", "GRUB2 bootloader lets an attacker bypass Secure Boot.")
        self.write("CVE-2020-1003", "U-Boot mishandles a boot image on the device.")
        self.write("CVE-2020-1004", "An unrelated flaw in a web application login form.")
        self.write("CVE-2020-1005", "A UEFI firmware bug.", state="REJECTED")
        self.out = Path(self.tmp.name) / "out"

    def write(self, cve_id: str, description: str, state: str = "PUBLISHED"):
        path = self.corpus / "cves" / "2020" / "1xxx" / f"{cve_id}.json"
        path.write_text(json.dumps(self.record(cve_id, description, state)))

    def tearDown(self):
        self.tmp.cleanup()

    def results(self, name: str) -> dict:
        return json.loads((self.out / f"{name}-results.json").read_text())

    def test_assigns_each_cve_to_the_right_type(self):
        proc = run_tool("classify_cves.py", "--cvelist", str(self.corpus),
                        "--output", str(self.out), "--jobs", "2")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("CVE-2020-1001", self.results("type1"))
        self.assertIn("CVE-2020-1002", self.results("type2"))
        self.assertIn("CVE-2020-1003", self.results("type3"))

    def test_unrelated_cve_is_not_collected(self):
        run_tool("classify_cves.py", "--cvelist", str(self.corpus),
                 "--output", str(self.out), "--jobs", "2")
        for name in TYPES:
            self.assertNotIn("CVE-2020-1004", self.results(name))

    def test_withdrawn_cve_is_skipped_and_counted(self):
        proc = run_tool("classify_cves.py", "--cvelist", str(self.corpus),
                        "--output", str(self.out), "--jobs", "2")
        self.assertIn("skipped 1 record(s) withdrawn upstream", proc.stdout)
        for name in TYPES:
            self.assertNotIn("CVE-2020-1005", self.results(name))

    def test_rejected_sentinel_survives_the_process_boundary(self):
        # A sentinel compared with `is` breaks once pickled to a worker; this
        # asserts the count actually arrives rather than crashing the unpack.
        proc = run_tool("classify_cves.py", "--cvelist", str(self.corpus),
                        "--output", str(self.out), "--jobs", "4")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_extracted_fields_match_the_dataset_schema(self):
        run_tool("classify_cves.py", "--cvelist", str(self.corpus),
                 "--output", str(self.out), "--jobs", "2")
        entry = self.results("type1")["CVE-2020-1001"]
        self.assertEqual(set(entry), {"cve_id", "description", "published_date",
                                      "vendor", "vuln_type", "file_path"})
        self.assertEqual(entry["vendor"], "ExampleCorp")
        self.assertEqual(entry["vuln_type"], "CWE-787: Out-of-bounds Write")

    def test_vendor_is_na_rather_than_guessed(self):
        record = self.record("CVE-2020-1006", "A BIOS SMM issue.")
        record["containers"]["cna"]["affected"] = [{"vendor": "n/a", "product": "n/a"}]
        (self.corpus / "cves" / "2020" / "1xxx" / "CVE-2020-1006.json").write_text(
            json.dumps(record))
        run_tool("classify_cves.py", "--cvelist", str(self.corpus),
                 "--output", str(self.out), "--jobs", "2")
        self.assertEqual(self.results("type1")["CVE-2020-1006"]["vendor"], "n/a")

    def test_overlap_report_flags_multi_type_cves(self):
        self.write("CVE-2020-1007", "aboot fails to validate the boot image.")
        run_tool("classify_cves.py", "--cvelist", str(self.corpus),
                 "--output", str(self.out), "--jobs", "2", "--report-overlaps")
        overlaps = json.loads((self.out / "type-overlaps.json").read_text())
        self.assertIn("CVE-2020-1007", overlaps)
        self.assertEqual(set(overlaps["CVE-2020-1007"]), {"type2", "type3"})


# ---------------------------------------------------------------------------
# Commit miner
# ---------------------------------------------------------------------------

class TestMinerParents(unittest.TestCase):
    """The parent link is the field a vulnerability benchmark depends on."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name) / "corpus"
        (self.base / "type1").mkdir(parents=True)
        self.repo = self.base / "type1" / "demo"
        self.hashes = make_repo(self.repo, [
            "initial commit",
            "add a feature",
            "fix a buffer overflow in the parser",
            "unrelated cleanup",
            "fix CVE-2024-1234: out-of-bounds read in the loader",
        ])
        self.out = Path(self.tmp.name) / "out"

    def tearDown(self):
        self.tmp.cleanup()

    def mine(self, *extra: str) -> dict:
        proc = run_tool("extract_vuln_commits.py", str(self.base),
                        "--output", str(self.out), "--jobs", "1", *extra)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads((self.out / "type1" / "demo.json").read_text())

    def test_parent_is_the_real_parent(self):
        data = self.mine()
        for entry in data["CVEs"] + data["vulnerability"]:
            expected = git(self.repo, "rev-list", "--parents", "-n", "1",
                           entry["commit"]).split()[1:]
            self.assertEqual(entry["parents"], expected)
            self.assertEqual(entry["parent"], expected[0])

    def test_parent_is_older_not_newer(self):
        data = self.mine()
        index = {h: i for i, h in enumerate(self.hashes)}
        for entry in data["CVEs"] + data["vulnerability"]:
            self.assertLess(index[entry["parent"]], index[entry["commit"]],
                            "parent must precede the commit, as the legacy field did not")

    def test_merge_parents_are_all_recorded(self):
        git(self.repo, "checkout", "-q", "-b", "side", self.hashes[0])
        (self.repo / "g.txt").write_text("x")
        git(self.repo, "add", "g.txt")
        git(self.repo, "commit", "-q", "-m", "side work",
            GIT_AUTHOR_DATE="2020-02-01T00:00:00+0000",
            GIT_COMMITTER_DATE="2020-02-01T00:00:00+0000")
        git(self.repo, "checkout", "-q", "main")
        git(self.repo, "merge", "-q", "--no-ff", "side", "-m",
            "Merge side: fixes a memory corruption bug",
            GIT_AUTHOR_DATE="2020-02-02T00:00:00+0000",
            GIT_COMMITTER_DATE="2020-02-02T00:00:00+0000")
        merge_hash = git(self.repo, "rev-parse", "HEAD")
        data = self.mine()
        entry = next(e for e in data["vulnerability"] if e["commit"] == merge_hash)
        self.assertEqual(len(entry["parents"]), 2, "both merge parents must be kept")


class TestMinerMatching(unittest.TestCase):
    """The false positives that dominated the published dataset must not return."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name) / "corpus"
        (self.base / "type2").mkdir(parents=True)
        self.repo = self.base / "type2" / "demo"
        make_repo(self.repo, [
            "initial commit",
            "OcApfsLib: Address review comments and some TODOs",
            "pe: tighten validity checks of DOS and PE headers",
            "rules: add symlinks also for dos partition table",
            "Make LinuxScan use msdos filesystem probing",
            "loader: fix a heap buffer overflow when parsing the config",
            "sbat: bump for CVE-2023-40547 and CVE-2023-40548",
            "net: mitigate a DoS triggered by a malformed packet",
        ])
        self.out = Path(self.tmp.name) / "out"
        proc = run_tool("extract_vuln_commits.py", str(self.base),
                        "--output", str(self.out), "--jobs", "1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.data = json.loads((self.out / "type2" / "demo.json").read_text())
        self.subjects = [e["message"].split("\n")[0]
                         for e in self.data["CVEs"] + self.data["vulnerability"]]

    def tearDown(self):
        self.tmp.cleanup()

    def test_todos_is_not_a_vulnerability(self):
        self.assertNotIn("OcApfsLib: Address review comments and some TODOs", self.subjects)

    def test_dos_the_operating_system_is_not_denial_of_service(self):
        self.assertNotIn("pe: tighten validity checks of DOS and PE headers", self.subjects)
        self.assertNotIn("rules: add symlinks also for dos partition table", self.subjects)
        self.assertNotIn("Make LinuxScan use msdos filesystem probing", self.subjects)

    def test_real_denial_of_service_acronym_still_matches(self):
        self.assertIn("net: mitigate a DoS triggered by a malformed packet", self.subjects)

    def test_real_vulnerability_matches(self):
        self.assertIn("loader: fix a heap buffer overflow when parsing the config",
                      self.subjects)

    def test_plural_forms_match(self):
        # Word boundaries alone dropped these; the substring matcher caught them
        # and they are real fixes.
        pats = kw.compile_vulnerability_patterns()
        for message in ["Prevent buffer overflows when writing to the terminal",
                        "elog: Fix race conditions in assigning platform log id",
                        "timer: Avoid integer overflows in usec calculations",
                        "tpm: fix failure caused by NULL pointers"]:
            with self.subTest(message=message):
                self.assertTrue(any(p.search(message) for _, p in pats), message)

    def test_plural_tolerance_does_not_match_longer_words(self):
        pats = kw.compile_vulnerability_patterns()
        for message in ["xive: Add more checks for exploitation mode",
                        "Address review comments and some TODOs"]:
            with self.subTest(message=message):
                self.assertFalse(any(p.search(message) for _, p in pats), message)

    def test_cve_ids_are_extracted_not_just_detected(self):
        entry = self.data["CVEs"][0]
        self.assertEqual(entry["cve_ids"], ["CVE-2023-40547", "CVE-2023-40548"])

    def test_matched_keywords_make_inclusion_auditable(self):
        entry = next(e for e in self.data["vulnerability"]
                     if "heap buffer overflow" in e["message"])
        self.assertIn("buffer overflow", entry["matched_keywords"])

    def test_cwe_tagging_requires_an_explicit_phrase(self):
        # token_set_ratio tagged "Bump version to 15.8" as CWE-680.
        self.assertEqual(miner.match_cwes("Bump version to 15.8"), [])
        self.assertEqual(miner.match_cwes("roms: only support SeaBIOS/SeaGRUB on x86"), [])
        tagged = miner.match_cwes("fix a null pointer dereference in the parser")
        self.assertEqual([t["CWE-ID"] for t in tagged], ["476"])


class TestMinerRobustness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name) / "corpus"
        (self.base / "type3").mkdir(parents=True)
        self.out = Path(self.tmp.name) / "out"

    def tearDown(self):
        self.tmp.cleanup()

    def mine(self):
        proc = run_tool("extract_vuln_commits.py", str(self.base),
                        "--output", str(self.out), "--jobs", "1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc, json.loads((self.out / "summary.json").read_text())

    def test_message_containing_the_legacy_delimiter_does_not_split_a_record(self):
        repo = self.base / "type3" / "tricky"
        make_repo(repo, [
            "initial commit",
            "fix use-after-free\n\n---END---\nnot a separate commit\nCVE-2021-9999",
        ])
        _, summary = self.mine()
        data = json.loads((self.out / "type3" / "tricky.json").read_text())
        # One commit, kept whole: the CVE in the body still belongs to it.
        self.assertEqual(len(data["CVEs"]), 1)
        self.assertEqual(data["CVEs"][0]["cve_ids"], ["CVE-2021-9999"])
        self.assertIn("---END---", data["CVEs"][0]["message"])

    def test_repo_with_no_findings_still_gets_a_summary_row(self):
        make_repo(self.base / "type3" / "clean", ["initial commit", "docs: typo"])
        _, summary = self.mine()
        self.assertIn("type3/clean", summary)
        self.assertEqual(summary["type3/clean"]["CVEs"], 0)
        self.assertEqual(summary["type3/clean"]["vulnerabilities"], 0)
        self.assertEqual(summary["type3/clean"]["commits_scanned"], 2)

    def test_non_repository_directory_is_skipped(self):
        make_repo(self.base / "type3" / "real", ["initial commit"])
        (self.base / "type3" / "NotARepo").mkdir()
        (self.base / "type3" / "NotARepo" / "x.txt").write_text("hi")
        proc, summary = self.mine()
        self.assertIn("skipping 1 non-repository", proc.stdout)
        self.assertNotIn("type3/NotARepo", summary)
        self.assertFalse((self.out / "type3" / "NotARepo.json").exists())

    def test_single_line_commit_message_is_not_dropped(self):
        make_repo(self.base / "type3" / "oneline", ["fix an integer overflow"])
        self.mine()
        data = json.loads((self.out / "type3" / "oneline.json").read_text())
        self.assertEqual(len(data["vulnerability"]), 1)

    def test_since_filter_narrows_the_scan(self):
        # make_repo dates commits 2020-01-01, -02, -03.  git's --since is
        # strictly exclusive at the boundary, so a bare "2020-01-03" would drop
        # the 2020-01-03T00:00:00 commit too; use an unambiguous instant.
        make_repo(self.base / "type3" / "dated",
                  ["initial", "fix a buffer overflow", "fix a double free"])
        proc = run_tool("extract_vuln_commits.py", str(self.base), "--output",
                        str(self.out), "--jobs", "1",
                        "--since", "2020-01-02T12:00:00+0000")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads((self.out / "type3" / "dated.json").read_text())
        self.assertEqual([e["message"] for e in data["vulnerability"]],
                         ["fix a double free"])


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

class TestCveStats(unittest.TestCase):
    def test_vendor_share_never_exceeds_100_percent(self):
        results = {f"CVE-2020-{i:04d}": {"cve_id": f"CVE-2020-{i:04d}", "description": "d",
                                         "published_date": "2020-01-01T00:00:00",
                                         "vendor": v, "vuln_type": "escalation of privilege"}
                   for i, v in enumerate(["Intel"] * 5 + ["Dell", "HP", "AMI"])}
        table = cve_stats.build_stats(results)
        import re
        shares = [float(m) for m in re.findall(r"(\d+\.\d+)%\)", table)]
        self.assertTrue(shares, "no vendor share rendered")
        for share in shares:
            self.assertLessEqual(share, 100.0)

    def test_normalization_merges_cwe_prefix_variants(self):
        self.assertEqual(cve_stats.normalize_vuln_type("CWE-20: Improper Input Validation"),
                         cve_stats.normalize_vuln_type("CWE-20 Improper Input Validation"))
        self.assertEqual(cve_stats.normalize_vuln_type("Denial of Service"),
                         cve_stats.normalize_vuln_type("denial of service"))

    def test_rows_sum_to_the_stated_total(self):
        results = {f"CVE-2020-{i:04d}": {"cve_id": f"CVE-2020-{i:04d}", "description": "d",
                                         "published_date": "2020-01-01T00:00:00",
                                         "vendor": "V", "vuln_type": t}
                   for i, t in enumerate(["a", "a", "b", "c", "n/a"])}
        table = cve_stats.build_stats(results)
        import re
        total = int(re.search(r"\*\*Total\*\* \| \*\*(\d+)\*\*", table).group(1))
        years = {y for y, _ in re.findall(r"^\|\s*(\d{4})\s*\|\s*(\d+)\s*\|", table, re.M)}
        rows = sum(int(c) for lbl, c in
                   re.findall(r"^\|\s*(?!\*\*Total|Vulnerability Type|-)([^|]+?)\s*\|\s*(\d+)\s*\|",
                              table, re.M) if lbl.strip() not in years)
        self.assertEqual(rows, total)

    @unittest.skipUnless(HAS_CVE_DB, "bootloader_cve_db not initialised")
    def test_no_normalize_reproduces_published_counts(self):
        results = json.loads((DB / "type1" / "type1-results.json").read_text())
        table = cve_stats.build_stats(results, normalize=False)
        for row in ["| escalation of privilege | 124 |",
                    "| cwe-20: improper input validation | 69 |",
                    "| cwe-119: improper restriction of operations within the bounds of a "
                    "memory buffer | 33 |"]:
            self.assertIn(row, table)


# ---------------------------------------------------------------------------
# Manifests and the tools index
# ---------------------------------------------------------------------------

class TestManifests(unittest.TestCase):
    """The JSON manifests drive both a script and a generated README."""

    TOOLS = json.loads((HERE / "analysis_tools.json").read_text()) \
        if (HERE / "analysis_tools.json").is_file() else []
    BOOTLOADERS = json.loads((HERE / "new_bootloaders.json").read_text()) \
        if (HERE / "new_bootloaders.json").is_file() else []

    def test_tool_manifest_is_well_formed(self):
        self.assertTrue(self.TOOLS, "analysis_tools.json is missing or empty")
        seen = set()
        for tool in self.TOOLS:
            with self.subTest(tool=tool.get("name")):
                for field in ("name", "slug", "category", "category_label",
                              "why", "url", "clone"):
                    self.assertTrue(tool.get(field), f"{field} missing")
                self.assertNotIn((tool["category"], tool["name"]), seen, "duplicate path")
                seen.add((tool["category"], tool["name"]))
                self.assertTrue(tool["clone"].endswith(".git"))

    def test_bootloader_manifest_is_well_formed(self):
        self.assertTrue(self.BOOTLOADERS, "new_bootloaders.json is missing or empty")
        seen = set()
        for entry in self.BOOTLOADERS:
            with self.subTest(bootloader=entry.get("name")):
                for field in ("name", "type", "slug", "why", "url", "clone"):
                    self.assertTrue(entry.get(field), f"{field} missing")
                self.assertIn(entry["type"], TYPES)
                self.assertNotIn((entry["type"], entry["name"]), seen, "duplicate path")
                seen.add((entry["type"], entry["name"]))

    def test_new_bootloaders_are_not_already_in_the_corpus(self):
        gitmodules = ROOT / "oss-bootloaders" / ".gitmodules"
        if not gitmodules.is_file():
            self.skipTest("oss-bootloaders not initialised")
        import configparser
        parser = configparser.ConfigParser()
        parser.read_string(gitmodules.read_text())
        existing = {parser.get(s, "path") for s in parser.sections()
                    if parser.has_option(s, "path")}
        for entry in self.BOOTLOADERS:
            path = f"{entry['type']}/{entry['name']}"
            # Once added, the manifest entry and the submodule agree; what must
            # never happen is the same name landing under two types.
            clashes = [p for p in existing
                       if p.rsplit("/", 1)[-1] == entry["name"] and p != path]
            self.assertEqual(clashes, [], f"{entry['name']} also present as {clashes}")

    def test_runner_manifest_covers_every_tool(self):
        runners = json.loads((HERE / "analysis_runners.json").read_text())
        self.assertEqual({r["name"] for r in runners}, {t["name"] for t in self.TOOLS},
                         "analysis_runners.json and analysis_tools.json disagree")

    def test_runnable_means_a_runner_script_exists(self):
        runners = json.loads((HERE / "analysis_runners.json").read_text())
        scripts = ROOT / "scripts" / "analysis" / "runners"
        for entry in runners:
            with self.subTest(tool=entry["name"]):
                has_script = bool(entry.get("runner")) and \
                    (scripts / entry["runner"]).is_file()
                if entry["status"] == "runnable":
                    self.assertTrue(has_script,
                                    f"{entry['name']} is 'runnable' with no runner script")
                if entry.get("runner"):
                    self.assertTrue((scripts / entry["runner"]).is_file(),
                                    f"{entry['runner']} is referenced but missing")

    def test_unrunnable_tools_say_why(self):
        runners = json.loads((HERE / "analysis_runners.json").read_text())
        for entry in runners:
            if entry["status"] in ("needs-license", "needs-hardware"):
                with self.subTest(tool=entry["name"]):
                    self.assertTrue(entry.get("blocker"),
                                    f"{entry['name']} is blocked but gives no reason")

    def test_build_recipes_name_real_bootloaders(self):
        recipes = json.loads((HERE / "build_commands.json").read_text())
        gitmodules = ROOT / "oss-bootloaders" / ".gitmodules"
        if not gitmodules.is_file():
            self.skipTest("oss-bootloaders not initialised")
        import configparser
        parser = configparser.ConfigParser()
        parser.read_string(gitmodules.read_text())
        names = {parser.get(s, "path").rsplit("/", 1)[-1]
                 for s in parser.sections() if parser.has_option(s, "path")}
        for recipe in recipes:
            with self.subTest(recipe=recipe["name"]):
                self.assertIn(recipe["name"], names,
                              f"build recipe for '{recipe['name']}' matches no bootloader")
                self.assertTrue(recipe.get("build"), "empty build command")

    def test_tool_categories_are_all_rendered(self):
        import generate_tools_table
        rendered = generate_tools_table.render(self.TOOLS)
        for tool in self.TOOLS:
            with self.subTest(tool=tool["name"]):
                self.assertIn(tool["name"], rendered)
            self.assertIn(tool["category"], generate_tools_table.ORDER)

    def test_every_tool_says_what_it_applies_to(self):
        runners = json.loads((HERE / "analysis_runners.json").read_text())
        for entry in runners:
            with self.subTest(tool=entry["name"]):
                self.assertTrue(entry.get("applies_to"),
                                f"{entry['name']} does not say which bootloaders it applies to")

    def test_overview_matches_the_manifest(self):
        overview = HERE / "OVERVIEW.md"
        if not overview.is_file():
            self.skipTest("OVERVIEW.md not generated yet")
        import generate_overview
        runners = json.loads((HERE / "analysis_runners.json").read_text())
        self.assertEqual(overview.read_text(), generate_overview.render(runners),
                         "tools/OVERVIEW.md is stale; re-run generate_overview.py")

    def test_generated_index_matches_the_manifest(self):
        index = ROOT / "analysis-tools" / "README.md"
        if not index.is_file():
            self.skipTest("analysis-tools/README.md not generated yet")
        import generate_tools_table
        self.assertEqual(index.read_text(), generate_tools_table.render(self.TOOLS),
                         "analysis-tools/README.md is stale; re-run "
                         "generate_tools_table.py")


# ---------------------------------------------------------------------------
# Literature search
# ---------------------------------------------------------------------------

class TestCollectPapers(unittest.TestCase):
    """Offline tests: matching and grouping, no dblp query."""

    PAPERS = [
        {"title": "BootStomp: On the Security of Bootloaders in Mobile Devices",
         "year": 2017, "venue": "USENIX Security", "url": ""},
        {"title": "FUZZUER: Enabling Fuzzing of UEFI Interfaces on EDK-2",
         "year": 2025, "venue": "NDSS", "url": ""},
        {"title": "SoK: All You Ever Wanted to Know About Bootloader Security",
         "year": 2026, "venue": "IEEE S&P", "url": ""},
        {"title": "DICE*: A Formally Verified Implementation of DICE Measured Boot",
         "year": 2021, "venue": "USENIX Security", "url": ""},
        {"title": "Stop Starving Me: Boosting Firmware Fuzzing Efficiency",
         "year": 2026, "venue": "IEEE S&P", "url": ""},
        {"title": "Leveraging Discrete CKKS to Bootstrap in High Precision",
         "year": 2025, "venue": "ACM CCS", "url": ""},
        {"title": "A neural machine translator to bootstrap GUI skeletons",
         "year": 2018, "venue": "ICSE", "url": ""},
        {"title": "Differential Inference Testing of Machine Learning Models",
         "year": 2019, "venue": "IEEE S&P", "url": ""},
    ]

    def matched(self, core_only=False):
        return {p["title"]: p for p in collect_papers.match(self.PAPERS, core_only)}

    def test_boot_papers_match_as_core(self):
        got = self.matched()
        for title in ["BootStomp: On the Security of Bootloaders in Mobile Devices",
                      "FUZZUER: Enabling Fuzzing of UEFI Interfaces on EDK-2",
                      "DICE*: A Formally Verified Implementation of DICE Measured Boot"]:
            self.assertIn(title, got)
            self.assertEqual(got[title]["tier"], "core")

    def test_bootstrap_in_the_crypto_and_ml_sense_is_rejected(self):
        # "bootstrap" matched FHE bootstrapping and ML bootstrapping and never
        # the boot chain, so it is not a keyword.  Same failure as "dos".
        got = self.matched()
        self.assertNotIn("Leveraging Discrete CKKS to Bootstrap in High Precision", got)
        self.assertNotIn("A neural machine translator to bootstrap GUI skeletons", got)

    def test_unrelated_paper_is_not_matched(self):
        self.assertNotIn("Differential Inference Testing of Machine Learning Models",
                         self.matched())

    def test_context_tier_catches_firmware_work(self):
        got = self.matched()
        entry = got["Stop Starving Me: Boosting Firmware Fuzzing Efficiency"]
        self.assertEqual(entry["tier"], "context")
        self.assertIn("firmware", entry["matched_context"])

    def test_core_only_drops_the_context_tier(self):
        self.assertNotIn("Stop Starving Me: Boosting Firmware Fuzzing Efficiency",
                         self.matched(core_only=True))

    def test_contribution_is_assigned_first_match_wins(self):
        cases = {
            "SoK: All You Ever Wanted to Know About Bootloader Security": "systematization",
            "BOOTKITTY: A Stealthy Bootkit-Rootkit Against Modern OSes": "attack",
            "FUZZUER: Enabling Fuzzing of UEFI Interfaces on EDK-2": "discovery",
            "DICE*: A Formally Verified Implementation of DICE Measured Boot": "defense",
            "Rehosting Embedded Firmware for Dynamic Analysis": "rehosting",
        }
        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertEqual(collect_papers.classify_contribution(title)[0], expected)

    def test_markdown_groups_by_contribution(self):
        table = collect_papers.render_markdown(collect_papers.match(self.PAPERS, False),
                                               2015, False)
        self.assertIn("## Systematization and measurement", table)
        self.assertIn("## Vulnerability discovery", table)
        self.assertIn("BootStomp", table)

    def test_top4grep_database_is_read_when_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "papers.db"
            conn = sqlite3.connect(db)
            conn.execute("CREATE TABLE paper (id INTEGER PRIMARY KEY, conference TEXT, "
                         "year INTEGER, title TEXT, authors TEXT, abstract TEXT)")
            conn.executemany("INSERT INTO paper (conference, year, title) VALUES (?,?,?)",
                             [("USENIX", 2017, "BootStomp: On the Security of Bootloaders"),
                              ("CCS", 2010, "Too old to be collected")])
            conn.commit(); conn.close()
            papers = collect_papers.read_top4grep(db, since=2015)
        self.assertEqual([p["title"] for p in papers],
                         ["BootStomp: On the Security of Bootloaders"])


# ---------------------------------------------------------------------------
# Inventory table
# ---------------------------------------------------------------------------

class TestGenerateTable(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "oss"
        (self.root / "type1").mkdir(parents=True)
        (self.root / ".gitmodules").write_text(
            '[submodule "type1/demo"]\n\tpath = type1/demo\n'
            '\turl = git@github.com:example/demo.git\n')
        self.out = Path(self.tmp.name) / "table.md"

    def tearDown(self):
        self.tmp.cleanup()

    def render(self) -> str:
        proc = run_tool("generate_table.py", "--root", str(self.root),
                        "--output", str(self.out))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return self.out.read_text()

    def test_header_typo_is_fixed(self):
        (self.root / "type1" / "demo").mkdir()
        table = self.render()
        self.assertIn("| Bootloader |", table)
        self.assertNotIn("Bootlaoder", table)

    def test_uninitialized_submodule_is_reported_as_such(self):
        (self.root / "type1" / "demo").mkdir()
        table = self.render()
        self.assertIn("not initialized", table)
        self.assertNotIn("N/A", table)

    def test_ssh_url_is_rewritten_for_the_browser(self):
        (self.root / "type1" / "demo").mkdir()
        self.assertIn("https://github.com/example/demo", self.render())

    def test_output_directory_is_created(self):
        (self.root / "type1" / "demo").mkdir()
        nested = Path(self.tmp.name) / "does" / "not" / "exist" / "table.md"
        proc = run_tool("generate_table.py", "--root", str(self.root),
                        "--output", str(nested))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(nested.is_file())

    def test_initialized_submodule_reports_real_commit_data(self):
        make_repo(self.root / "type1" / "demo", ["initial commit", "second"])
        table = self.render()
        self.assertNotIn("not initialized", table)
        self.assertIn("| 2 |", table)   # commit count


if __name__ == "__main__":
    unittest.main(verbosity=2)
