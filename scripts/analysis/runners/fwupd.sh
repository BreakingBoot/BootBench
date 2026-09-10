#!/usr/bin/env bash
# Parse a firmware blob with fwupd's offline tooling.
#
#   run-tool.sh fwupd <firmware> [--type TYPE] [--extract] [--output DIR]
#
# fwupd's main job is updating firmware on the running machine, which needs
# real hardware and a privileged daemon. But fwupdtool also parses firmware
# offline: `firmware-parse` identifies the container format and prints its
# structure, `firmware-extract` unpacks it. That half runs in a container and
# tells you how fwupd would interpret an image it was asked to flash.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

IMG=""; OUT=""; EXTRACT=0; TYPE=""
while [ $# -gt 0 ]; do
    case "$1" in
        --type) TYPE="$2"; shift ;;
        --extract) EXTRACT=1 ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) IMG="$1" ;;
    esac
    shift
done
[ -n "$IMG" ] && [ -f "$IMG" ] || die "usage: run-tool.sh fwupd <firmware>"
need_docker
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"
NAME="$(basename "$IMG")"
OUT="${OUT:-$ROOT/analysis-results/fwupd/$NAME}"; mkdir -p "$OUT"; check_mount "$OUT"
# A runner that die()s partway leaves root-owned output behind, which the
# invoking user then cannot delete. Reclaim on any exit, not just success.
trap 'reclaim_output "$OUT"' EXIT

IMAGE=bootbench/fwupd
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    say "Building $IMAGE (first run only)"
    docker build -q -t "$IMAGE" - >/dev/null <<'DOCKER'
FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends fwupd \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
DOCKER
fi

# firmware-parse prompts for the container format if it is not told one.
# Guess from the file: a UEFI application is a PE, a .fd is a firmware volume.
if [ -z "$TYPE" ]; then
    case "$(file -b "$IMG")" in
        *PE32*|*MS-DOS*) TYPE=pefile ;;
        *)               TYPE=efi-volume ;;
    esac
    say "no --type given; using $TYPE"
fi

say "fwupdtool firmware-parse on $NAME as $TYPE"
docker run --rm -v "$IMG:/work/image:ro" -v "$OUT:/out" "$IMAGE" bash -c '
    echo "== firmware-parse =="
    fwupdtool firmware-parse /work/image '"$TYPE"' 2>&1 | head -60
    echo; echo "== supported firmware formats =="
    fwupdtool get-firmware-types 2>&1 | head -30
' | tee "$OUT/parse.txt"

if [ "$EXTRACT" = "1" ]; then
    say "fwupdtool firmware-extract"
    docker run --rm -v "$IMG:/work/image:ro" -v "$OUT:/out" "$IMAGE" bash -c '
        cd /out && fwupdtool firmware-extract /work/image '"$TYPE"' 2>&1 | tail -20' \
        | tee -a "$OUT/parse.txt"
fi
say "Output: $OUT/parse.txt"
