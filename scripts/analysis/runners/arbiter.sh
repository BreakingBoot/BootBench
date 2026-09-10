#!/usr/bin/env bash
# Detect a bug class in a bootloader binary with Arbiter.
#
#   run-tool.sh arbiter <binary> [--template FILE] [--output DIR]
#
# Arbiter needs a "vulnerability description" template naming the sinks and the
# constraint that makes a value dangerous. The templates it ships target the
# Juliet test suite and match nothing in real firmware, so this defaults to
# scripts/analysis/templates/bootloader_CWE190.py: integer overflow reaching a
# UEFI, U-Boot or libc allocation or copy.
#
# The image applies scripts/analysis/patches/arbiter-angr-api.patch, without
# which arbiter cannot import under angr 9.2.x.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

BIN=""; OUT=""; TEMPLATE=""
while [ $# -gt 0 ]; do
    case "$1" in
        --template) TEMPLATE="$2"; shift ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) BIN="$1" ;;
    esac
    shift
done
[ -n "$BIN" ] && [ -f "$BIN" ] || die "usage: run-tool.sh arbiter <binary>"
need_docker
BIN="$(cd "$(dirname "$BIN")" && pwd)/$(basename "$BIN")"
NAME="$(basename "$BIN")"
TEMPLATE="${TEMPLATE:-$ANALYSIS_DIR/templates/bootloader_CWE190.py}"
[ -f "$TEMPLATE" ] || die "template not found: $TEMPLATE"
TEMPLATE="$(cd "$(dirname "$TEMPLATE")" && pwd)/$(basename "$TEMPLATE")"
OUT="${OUT:-$ROOT/analysis-results/arbiter/$NAME}"; mkdir -p "$OUT"; check_mount "$OUT"
# A runner that die()s partway leaves root-owned output behind, which the
# invoking user then cannot delete. Reclaim on any exit, not just success.
trap 'reclaim_output "$OUT"' EXIT

SRC="$ROOT/analysis-tools/static/arbiter"
[ -f "$SRC/setup.py" ] || die "arbiter submodule not checked out. Run:
    git submodule update --init analysis-tools/static/arbiter"

IMAGE=bootbench/arbiter
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    say "Building $IMAGE (first run only)"
    tmp="$OUT/.build"; rm -rf "$tmp"; mkdir -p "$tmp"
    cp -a "$SRC/." "$tmp/"
    git -C "$tmp" apply "$ANALYSIS_DIR/patches/arbiter-angr-api.patch" 2>/dev/null \
        || patch -p1 -d "$tmp" < "$ANALYSIS_DIR/patches/arbiter-angr-api.patch" >/dev/null \
        || die "could not apply arbiter-angr-api.patch"
    say "applied arbiter-angr-api.patch"
    docker build -q -t "$IMAGE" "$tmp" >/dev/null
    rm -rf "$tmp"
fi

say "Running arbiter on $NAME with $(basename "$TEMPLATE")"
docker run --rm -v "$BIN:/home/test/bins/target:ro" -v "$TEMPLATE:/home/test/vd.py:ro" \
    -v "$OUT:/out" "$IMAGE" bash -eo pipefail -c '
        cd /home/test
        export ARBITER_OUT=/out
        python3 vuln_templates/run_arbiter.py -f vd.py -t bins/target -l /out 2>&1 | tail -40
    ' | tee "$OUT/arbiter.txt"
say "Output: $OUT/arbiter.txt"
