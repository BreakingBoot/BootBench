#!/usr/bin/env bash
# Run chipsec's offline UEFI analysis over a firmware image.
#
#   run-tool.sh chipsec <image> [--output DIR]
#
# chipsec's headline value is on-target: chipsec_main loads a kernel driver and
# reads MSRs, SPI protection and SMM state on the live platform, which cannot
# be done from a container. This runner covers the offline half -- chipsec_util
# decoding a firmware image and listing its contents -- which does work on a
# build from the corpus.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

IMG=""; OUT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) IMG="$1" ;;
    esac
    shift
done
[ -n "$IMG" ] && [ -f "$IMG" ] || die "usage: run-tool.sh chipsec <firmware-image>"
need_docker
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"
NAME="$(basename "$IMG")"
OUT="${OUT:-$ROOT/analysis-results/chipsec/$NAME}"; mkdir -p "$OUT"
check_mount "$OUT"
# A runner that die()s partway leaves root-owned output behind, which the
# invoking user then cannot delete. Reclaim on any exit, not just success.
trap 'reclaim_output "$OUT"' EXIT

IMAGE=bootbench/chipsec
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    say "Building $IMAGE (first run only)"
    docker build -q -t "$IMAGE" - >/dev/null <<'DOCKER'
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      git build-essential linux-headers-generic nasm && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir chipsec brotli
WORKDIR /work
DOCKER
fi

say "chipsec_util uefi decode on $NAME (offline)"
docker run --rm -v "$IMG:/work/image:ro" -v "$OUT:/out" "$IMAGE" bash -eo pipefail -c '
    cd /out && cp /work/image ./image
    chipsec_util -n uefi decode ./image 2>&1 | tail -40
    rm -f ./image
' | tee "$OUT/decode.txt"
say "Output: $OUT/decode.txt"
