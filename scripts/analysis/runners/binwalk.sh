#!/usr/bin/env bash
# Extract and identify structures inside a firmware image.
#
#   run-tool.sh binwalk <image> [--extract] [--output DIR]
#
# Takes a built firmware image, not source: the first step when the artefact
# is a flash dump rather than a repository.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

IMG=""; OUT=""; EXTRACT=0
while [ $# -gt 0 ]; do
    case "$1" in
        --extract) EXTRACT=1 ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,8p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) IMG="$1" ;;
    esac
    shift
done
[ -n "$IMG" ] && [ -f "$IMG" ] || die "usage: run-tool.sh binwalk <firmware-image>"
need_docker
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"
NAME="$(basename "$IMG")"
OUT="${OUT:-$ROOT/analysis-results/binwalk/$NAME}"; mkdir -p "$OUT"
check_mount "$OUT"

IMAGE=bootbench/binwalk
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    say "Building $IMAGE (first run only)"
    docker build -q -t "$IMAGE" - >/dev/null <<'DOCKER'
FROM rust:1-slim-bookworm
# binwalk v3 pulls in fontconfig through its entropy-plot dependency, which
# needs pkg-config and the fontconfig headers at build time.
RUN apt-get update && apt-get install -y --no-install-recommends \
      git ca-certificates p7zip-full zstd unzip \
      pkg-config libfontconfig1-dev libfreetype-dev \
 && rm -rf /var/lib/apt/lists/*
RUN cargo install binwalk --locked
WORKDIR /work
DOCKER
fi

say "Scanning $NAME"
if [ "$EXTRACT" = "1" ]; then
    docker run --rm -v "$IMG:/work/image:ro" -v "$OUT:/out" "$IMAGE" \
        binwalk --extract --directory /out /work/image | tee "$OUT/scan.txt"
else
    docker run --rm -v "$IMG:/work/image:ro" "$IMAGE" \
        binwalk /work/image | tee "$OUT/scan.txt"
fi
reclaim_output "$OUT"
say "Output: $OUT/scan.txt"
