#!/usr/bin/env bash
# Summarise a UEFI image with fiano's utk: the firmware volume tree.
#
#   run-tool.sh fiano <image> [--output DIR]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

IMG=""; OUT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,5p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) IMG="$1" ;;
    esac
    shift
done
[ -n "$IMG" ] && [ -f "$IMG" ] || die "usage: run-tool.sh fiano <image>"
need_docker
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"
NAME="$(basename "$IMG")"
OUT="${OUT:-$ROOT/analysis-results/fiano/$NAME}"; mkdir -p "$OUT"
check_mount "$OUT"
# A runner that die()s partway leaves root-owned output behind, which the
# invoking user then cannot delete. Reclaim on any exit, not just success.
trap 'reclaim_output "$OUT"' EXIT

IMAGE=bootbench/fiano
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    say "Building $IMAGE (first run only)"
    docker build -q -t "$IMAGE" - >/dev/null <<'DOCKER'
FROM golang:1.23-bookworm
RUN go install github.com/linuxboot/fiano/cmds/utk@latest
WORKDIR /work
DOCKER
fi

say "Running utk over $NAME"
docker run --rm -v "$IMG:/work/image:ro" -v "$OUT:/out" "$IMAGE" \
    utk /work/image table | tee "$OUT/table.txt"
say "Output: $OUT/table.txt"
