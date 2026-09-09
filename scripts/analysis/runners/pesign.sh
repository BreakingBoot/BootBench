#!/usr/bin/env bash
# Inspect the Authenticode signatures on a UEFI PE binary.
#
#   run-tool.sh pesign <module.efi> [--output DIR]
#
# Shows whether a bootloader stage is signed and by whom -- the Secure Boot
# chain as it actually exists on a machine, rather than as configured.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

MOD=""; OUT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,8p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) MOD="$1" ;;
    esac
    shift
done
[ -n "$MOD" ] && [ -f "$MOD" ] || die "usage: run-tool.sh pesign <module.efi>"
need_docker
MOD="$(cd "$(dirname "$MOD")" && pwd)/$(basename "$MOD")"
NAME="$(basename "$MOD")"
OUT="${OUT:-$ROOT/analysis-results/pesign/$NAME}"; mkdir -p "$OUT"
check_mount "$OUT"

IMAGE=bootbench/pesign
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    say "Building $IMAGE (first run only)"
    docker build -q -t "$IMAGE" - >/dev/null <<'DOCKER'
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends pesign sbsigntool osslsigncode \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
DOCKER
fi

say "Signature check on $NAME"
docker run --rm -v "$MOD:/work/module:ro" "$IMAGE" bash -c '
    echo "== sbverify --list =="; sbverify --list /work/module 2>&1 || true
    echo; echo "== pesign -S =="; pesign -i /work/module -S 2>&1 || true
' | tee "$OUT/signatures.txt"
reclaim_output "$OUT"
say "Output: $OUT/signatures.txt"
