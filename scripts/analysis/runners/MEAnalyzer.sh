#!/usr/bin/env bash
# Analyse an Intel ME / CSME / TXE firmware region.
#
#   run-tool.sh MEAnalyzer <me-region.bin> [--output DIR]
#
# Takes an ME region, not a whole flash image: split one out with
# UEFIExtract or uefi-firmware-parser first. The ME region is a distinct
# processor's firmware sitting beside the bootloader in the same flash part,
# which is why it is in scope here at all.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

IMG=""; OUT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) IMG="$1" ;;
    esac
    shift
done
[ -n "$IMG" ] && [ -f "$IMG" ] || die "usage: run-tool.sh MEAnalyzer <me-region.bin>"
need_docker
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"
NAME="$(basename "$IMG")"
OUT="${OUT:-$ROOT/analysis-results/MEAnalyzer/$NAME}"; mkdir -p "$OUT"
check_mount "$OUT"

SRC="$ROOT/analysis-tools/inspection/MEAnalyzer"
[ -f "$SRC/MEA.py" ] || die "MEAnalyzer submodule not checked out. Run:
    git submodule update --init analysis-tools/inspection/MEAnalyzer"

IMAGE=bootbench/pytools
build_image_if_needed "$IMAGE" "$ANALYSIS_DIR/docker/pytools.Dockerfile"

say "Analysing $NAME"
docker run --rm -t -v "$SRC:/mea:ro" -v "$IMG:/work/image:ro" -v "$OUT:/out" "$IMAGE" \
    bash -eo pipefail -c '
        pip install --quiet colorama pltable crccheck >/dev/null 2>&1 || true
        cp -a /mea /tmp/mea && cd /tmp/mea
        python3 MEA.py -skip -exit /work/image 2>&1
    ' | tee "$OUT/analysis.txt"
reclaim_output "$OUT"
say "Output: $OUT/analysis.txt"
