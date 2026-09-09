#!/usr/bin/env bash
# Run every BootBench tool and report what each one produced.
#
#   ./scripts/run-all-tools.sh [--output DIR] [--cvelist PATH] [--skip-network]
#
# Read-only by default: everything is written under --output (a scratch
# directory), never into the submodules. Use the update-*.sh scripts to
# actually publish a refresh.
#
# Exit status is non-zero if a tool fails. Dataset validation findings are
# reported but do not fail the run -- they are data problems, not tool
# problems; see tools/docs/improvements.md.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

usage() { sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

OUT=""; CVELIST=""; SKIP_NET=0; ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --output) OUT="$2"; shift ;;
        --cvelist) CVELIST="$2"; shift ;;
        --skip-network) SKIP_NET=1 ;;
        *) ARGS+=("$1") ;;
    esac
    shift
done
parse_common_args ${ARGS[@]+"${ARGS[@]}"}
OUT="${OUT:-${TMPDIR:-/tmp}/bootbench-run}"
mkdir -p "$OUT"

FAILED=(); RAN=(); SKIPPED=()

step() {  # step <name> <command...>
    local name="$1"; shift
    say "$name"
    if "$@" > "$OUT/$name.log" 2>&1; then
        RAN+=("$name")
        tail -3 "$OUT/$name.log" | sed 's/^/    /'
    else
        FAILED+=("$name")
        printf '\033[1;31m    FAILED\033[0m (see %s)\n' "$OUT/$name.log"
        tail -8 "$OUT/$name.log" | sed 's/^/    /'
    fi
}

skip() { SKIPPED+=("$1"); warn "$1: $2"; }

say "Output directory: $OUT"
echo

# --- 1. the test suite -----------------------------------------------------
step test_tools "$PYTHON" "$TOOLS/test_tools.py"

# --- 2. dataset validation (findings are data problems, not failures) ------
say "validate_dataset"
if "$PYTHON" "$TOOLS/validate_dataset.py" --root "$ROOT" > "$OUT/validate_dataset.log" 2>&1; then
    RAN+=(validate_dataset); echo "    all checks passed"
else
    RAN+=(validate_dataset)
    grep -cE '^\s+.?\[?[0-9;]*m?FAIL' "$OUT/validate_dataset.log" >/dev/null 2>&1 || true
    tail -1 "$OUT/validate_dataset.log" | sed 's/\x1b\[[0-9;]*m//g;s/^/    /'
    echo "    (dataset findings, not tool failures -- see tools/docs/improvements.md)"
fi
echo

# --- 3. inventory table ----------------------------------------------------
if [ -e "$ROOT/oss-bootloaders/.git" ]; then
    step generate_table "$PYTHON" "$TOOLS/generate_table.py" \
        --root "$ROOT/oss-bootloaders" --output "$OUT/table.md"
else
    skip generate_table "oss-bootloaders is not checked out"
fi
echo

# --- 4. commit miner -------------------------------------------------------
repos=$(find "$ROOT/oss-bootloaders"/type[123] -mindepth 1 -maxdepth 1 -type d \
        -exec test -e '{}/.git' ';' -print 2>/dev/null | wc -l | tr -d ' ')
if [ "${repos:-0}" != "0" ]; then
    step extract_vuln_commits "$PYTHON" "$TOOLS/extract_vuln_commits.py" \
        "$ROOT/oss-bootloaders" --output "$OUT/commits"
else
    skip extract_vuln_commits "no bootloader submodules checked out (git -C oss-bootloaders submodule update --init --recursive)"
fi
echo

# --- 5. CVE statistics, over the published data ----------------------------
if [ -f "$ROOT/bootloader_cve_db/type1/type1-results.json" ]; then
    for t in type1 type2 type3; do
        step "cve_stats-$t" "$PYTHON" "$TOOLS/cve_stats.py" \
            --input "$ROOT/bootloader_cve_db/$t/$t-results.json" \
            --stats "$OUT/$t-stats.md" \
            --output "$OUT/$t-cves" \
            --source-dir "$ROOT/bootloader_cve_db/$t/cves"
    done
else
    skip cve_stats "bootloader_cve_db is not checked out"
fi
echo

# --- 6. CVE classifier -----------------------------------------------------
if [ -n "$CVELIST" ] && [ -d "$CVELIST/cves" ]; then
    step classify_cves "$PYTHON" "$TOOLS/classify_cves.py" \
        --cvelist "$CVELIST" --output "$OUT/cves" --report-overlaps
elif [ -d "$ROOT/bootloader_cve_db/type1/cves" ]; then
    # Re-classify the published records: exercises the full path without a
    # multi-gigabyte clone, and should re-derive the published labels.
    say "classify_cves (no --cvelist; replaying the published records instead)"
    rm -rf "$OUT/replay"; mkdir -p "$OUT/replay/cves"
    cp "$ROOT"/bootloader_cve_db/type[123]/cves/*.json "$OUT/replay/cves/" 2>/dev/null || true
    step classify_cves "$PYTHON" "$TOOLS/classify_cves.py" \
        --cvelist "$OUT/replay" --output "$OUT/cves" --report-overlaps
else
    skip classify_cves "needs --cvelist or a checked-out bootloader_cve_db"
fi
echo

# --- 7. literature search --------------------------------------------------
if [ "$SKIP_NET" = "1" ]; then
    skip collect_papers "--skip-network given"
else
    step collect_papers "$PYTHON" "$TOOLS/collect_papers.py" \
        --output "$OUT/papers.json" --markdown "$OUT/PAPERS.md"
fi
echo

# --- summary ---------------------------------------------------------------
say "Summary"
printf '    ran:     %s\n' "${RAN[*]:-none}"
[ ${#SKIPPED[@]} -gt 0 ] && printf '    skipped: %s\n' "${SKIPPED[*]}"
if [ ${#FAILED[@]} -gt 0 ]; then
    printf '\033[1;31m    failed:  %s\033[0m\n' "${FAILED[*]}"
    echo "    logs in $OUT"
    exit 1
fi
echo "    all tools ran; logs and output in $OUT"
