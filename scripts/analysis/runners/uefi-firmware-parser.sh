#!/usr/bin/env bash
# Parse a UEFI firmware image: volumes, files, sections and the flash descriptor.
#
#   run-tool.sh uefi-firmware-parser <image> [--extract] [--output DIR]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

IMG=""; OUT=""; EXTRACT=0
while [ $# -gt 0 ]; do
    case "$1" in
        --extract) EXTRACT=1 ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,5p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) IMG="$1" ;;
    esac
    shift
done
[ -n "$IMG" ] && [ -f "$IMG" ] || die "usage: run-tool.sh uefi-firmware-parser <image>"
need_docker
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"
NAME="$(basename "$IMG")"
OUT="${OUT:-$ROOT/analysis-results/uefi-firmware-parser/$NAME}"; mkdir -p "$OUT"
check_mount "$OUT"

IMAGE=bootbench/pytools
build_image_if_needed "$IMAGE" "$ANALYSIS_DIR/docker/pytools.Dockerfile"

flags="-b"; [ "$EXTRACT" = "1" ] && flags="-b -e -o /out/extracted"
say "Parsing $NAME"
docker run --rm -v "$IMG:/work/image:ro" -v "$OUT:/out" "$IMAGE" bash -eo pipefail -c "
    pip install --quiet uefi-firmware >/dev/null 2>&1 || pip install uefi-firmware
    uefi-firmware-parser $flags /work/image
" | tee "$OUT/parse.txt"
reclaim_output "$OUT"
say "Output: $OUT/parse.txt"
