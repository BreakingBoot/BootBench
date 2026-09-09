#!/usr/bin/env bash
# Extract executable UEFI modules from a firmware image with UEFI_RETool.
#
#   run-tool.sh uefi_retool <image> [--output DIR]
#
# Only the IDA-free half of the tool. UEFI_RETool's `get-info` and `get-pp`
# commands drive IDA Pro to recover protocols and proprietary GUIDs; those
# cannot run here. `get-images` uses uefi-firmware-parser and does, giving you
# the per-module executables the other tools consume.
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
[ -n "$IMG" ] && [ -f "$IMG" ] || die "usage: run-tool.sh uefi_retool <image>"
need_docker
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"
NAME="$(basename "$IMG")"
OUT="${OUT:-$ROOT/analysis-results/uefi_retool/$NAME}"; mkdir -p "$OUT"; check_mount "$OUT"

SRC="$ROOT/analysis-tools/inspection/uefi_retool"
[ -f "$SRC/uefi_retool.py" ] || die "uefi_retool submodule not checked out. Run:
    git submodule update --init analysis-tools/inspection/uefi_retool"

IMAGE=bootbench/uefi-retool
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    say "Building $IMAGE (first run only)"
    docker build -q -t "$IMAGE" -f - "$SRC" >/dev/null <<'DOCKER'
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential \
 && rm -rf /var/lib/apt/lists/*
COPY . /src
RUN pip install --no-cache-dir click colorama terminaltables tqdm uefi-firmware
WORKDIR /src
DOCKER
fi

say "Extracting modules from $NAME"
docker run --rm -v "$IMG:/work/image:ro" -v "$OUT:/out" "$IMAGE" bash -eo pipefail -c '
    cd /src && python3 uefi_retool.py get-images /work/image 2>&1 | tail -20
    if [ -d modules ]; then cp -a modules /out/ && echo "modules: $(ls modules | wc -l)"; fi
' | tee "$OUT/extract.txt"
reclaim_output "$OUT"
[ -d "$OUT/modules" ] && say "$(ls "$OUT/modules" | wc -l) modules -> $OUT/modules"
say "Output: $OUT/extract.txt"
