#!/usr/bin/env bash
# Run BootStomp's taint analysis over an Android bootloader image.
#
#   run-tool.sh BootStomp [config] [--list] [--output DIR]
#
# BootStomp is not a general tool: it analyses Android bootloaders using a
# per-image config that supplies the architecture, thumb mode and the address
# of the unlock check. It ships those configs and the matching images, so the
# default target is its own Qualcomm LK -- the same bootloader the corpus
# carries as type2/lk.
#
# A run takes roughly 30 minutes. Uses the authors' prebuilt image
# (badnack/bootstomp); the repository's own Dockerfile is just FROM that.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

CONFIG="config.qualcomm.unpatch"; OUT=""; LIST=0
while [ $# -gt 0 ]; do
    case "$1" in
        --list) LIST=1 ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) CONFIG="$1" ;;
    esac
    shift
done
need_docker
SRC="$ROOT/analysis-tools/static/BootStomp"
[ -d "$SRC/config" ] || die "BootStomp submodule not checked out. Run:
    git submodule update --init analysis-tools/static/BootStomp"

if [ "$LIST" = "1" ]; then
    say "Available configs and their images"
    for c in "$SRC"/config/*; do
        img=$("$PYTHON" -c "import json,sys;print(json.load(open(sys.argv[1])).get('bootloader','?'))" "$c" 2>/dev/null)
        printf "  %-26s %s\n" "$(basename "$c")" "$img"
    done
    exit 0
fi
[ -f "$SRC/config/$CONFIG" ] || die "no such config: $CONFIG
    List them with: run-tool.sh BootStomp --list"

OUT="${OUT:-$ROOT/analysis-results/BootStomp/$CONFIG}"; mkdir -p "$OUT"; check_mount "$OUT"
# A runner that die()s partway leaves root-owned output behind, which the
# invoking user then cannot delete. Reclaim on any exit, not just success.
trap 'reclaim_output "$OUT"' EXIT

IMAGE=badnack/bootstomp
docker image inspect "$IMAGE" >/dev/null 2>&1 || { say "Pulling $IMAGE (first run only)"; docker pull -q "$IMAGE" >/dev/null; }

# The image already contains a BootStomp checkout and an angr virtualenv,
# both owned by the `angr` user. Use those rather than mounting our own copy:
# angr lives in /home/angr/.virtualenvs/angr and is not on the default PATH.
say "Taint analysis with $CONFIG (this takes about 30 minutes)"
docker run --rm -u angr -v "$OUT:/out" "$IMAGE" bash -lc "
    source /home/angr/.virtualenvs/angr/bin/activate
    cd /home/angr/BootStomp
    python taint_analysis/bootloadertaint.py config/$CONFIG 2>&1 | tail -30
    for f in /tmp/BootloaderTaint_*; do
        [ -e \"\$f\" ] || continue
        cp \"\$f\" /out/ 2>/dev/null || true
        echo '=== pretty printed ==='
        python taint_analysis/result_pretty_print.py \"\$f\" 2>&1 | tail -50
    done
" | tee "$OUT/taint.txt"
say "Output: $OUT/taint.txt"
