#!/usr/bin/env bash
# Dump the structure of a UEFI image with UEFIExtract (UEFITool NE).
#
#   run-tool.sh UEFITool <image> [--extract] [--output DIR]
#
# Produces a report of every firmware volume, file and section. --extract also
# writes each file out, which is how you get the individual DXE modules that
# fwhunt-scan and angr then consume.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

IMG=""; OUT=""; EXTRACT=0
while [ $# -gt 0 ]; do
    case "$1" in
        --extract) EXTRACT=1 ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) IMG="$1" ;;
    esac
    shift
done
[ -n "$IMG" ] && [ -f "$IMG" ] || die "usage: run-tool.sh UEFITool <image>"
need_docker
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"
NAME="$(basename "$IMG")"
OUT="${OUT:-$ROOT/analysis-results/UEFITool/$NAME}"; mkdir -p "$OUT"
check_mount "$OUT"

IMAGE=bootbench/uefitool
UEFITOOL_SRC="$ROOT/analysis-tools/inspection/UEFITool"
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    [ -f "$UEFITOOL_SRC/UEFIExtract/CMakeLists.txt" ] || die "UEFITool submodule not checked out. Run:
    git submodule update --init analysis-tools/inspection/UEFITool"
    say "Building $IMAGE from the submodule (first run only)"
    # The top-level CMakeLists pulls in Qt6 for the GUI; UEFIExtract has its
    # own, so build that subdirectory directly and keep the image small.
    docker build -q -t "$IMAGE" -f - "$UEFITOOL_SRC" >/dev/null <<'DOCKER'
FROM debian:bookworm-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
      cmake build-essential zlib1g-dev && rm -rf /var/lib/apt/lists/*
COPY . /src
RUN cmake -S /src/UEFIExtract -B /build -DCMAKE_BUILD_TYPE=Release \
 && cmake --build /build -j"$(nproc)" \
 && cp /build/uefiextract /usr/local/bin/UEFIExtract

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends zlib1g \
 && rm -rf /var/lib/apt/lists/*
COPY --from=build /usr/local/bin/UEFIExtract /usr/local/bin/UEFIExtract
WORKDIR /work
DOCKER
fi

mode="report"; [ "$EXTRACT" = "1" ] && mode="unpack"
say "UEFIExtract $mode on $NAME"
docker run --rm -v "$IMG:/work/image:ro" -v "$OUT:/out" "$IMAGE" bash -eo pipefail -c "
    cp /work/image /out/image && cd /out && UEFIExtract image $mode
    rm -f /out/image
"
reclaim_output "$OUT"
if [ -f "$OUT/image.report.txt" ]; then
    mv "$OUT/image.report.txt" "$OUT/report.txt"
    say "$(wc -l < "$OUT/report.txt") entries -> $OUT/report.txt"
fi
# An `[ test ] && { ... }` as the final statement makes the script exit 1
# whenever the test is false, which for report mode it always is.
if [ -d "$OUT/image.dump" ]; then
    mv "$OUT/image.dump" "$OUT/dump"
    say "files extracted to $OUT/dump"
fi
