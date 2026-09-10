#!/usr/bin/env bash
# Run Karonte's multi-binary taint analysis over a bootloader.
#
#   run-tool.sh karonte [config] [--list] [--output DIR]
#
# Karonte is driven by a per-firmware JSON config giving the binaries, the load
# address and the entry source. It ships configs for Qualcomm's Little Kernel
# -- the bootloader the corpus carries as type2/lk -- but not the binaries
# themselves. BootStomp, from the same group, does ship them, so this stages
# them across.
#
# Karonte's own checkout is pinned to an angr generation that no longer
# installs; this uses the authors' badnack/karonte image, whose virtualenv is
# not on the default PATH.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

CONFIG="lk_unpatched.config.json"; OUT=""; LIST=0
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
SRC="$ROOT/analysis-tools/static/karonte"
BS="$ROOT/analysis-tools/static/BootStomp"
[ -d "$SRC/config" ] || die "karonte submodule not checked out. Run:
    git submodule update --init analysis-tools/static/karonte"

if [ "$LIST" = "1" ]; then
    say "Bootloader configs (others target routers, not bootloaders)"
    for c in "$SRC"/config/lk/*.json; do
        printf "  %-28s %s\n" "$(basename "$c")" \
            "$("$PYTHON" -c "import json,sys;print(json.load(open(sys.argv[1]))['bin'])" "$c" 2>/dev/null)"
    done
    exit 0
fi
[ -f "$SRC/config/lk/$CONFIG" ] || die "no such config: $CONFIG
    List them with: run-tool.sh karonte --list"

OUT="${OUT:-$ROOT/analysis-results/karonte/${CONFIG%.config.json}}"; mkdir -p "$OUT"; check_mount "$OUT"
# A runner that die()s partway leaves root-owned output behind, which the
# invoking user then cannot delete. Reclaim on any exit, not just success.
trap 'reclaim_output "$OUT"' EXIT

# The config names ./firmware/lk/<name>; BootStomp ships exactly those files.
BIN=$("$PYTHON" -c "import json,sys;print(json.load(open(sys.argv[1]))['bin'][0])" "$SRC/config/lk/$CONFIG")
BINNAME="$(basename "$BIN")"
SRCBIN="$BS/bootloaders/qualcomm_lk/$BINNAME"
[ -f "$SRCBIN" ] || die "karonte's config wants $BINNAME, which it does not ship.
    BootStomp has it; check that submodule out:
    git submodule update --init analysis-tools/static/BootStomp"

STAGE="$OUT/firmware/lk"; mkdir -p "$STAGE"; cp -f "$SRCBIN" "$STAGE/$BINNAME"
say "staged $BINNAME from BootStomp"

IMAGE=badnack/karonte
docker image inspect "$IMAGE" >/dev/null 2>&1 || { say "Pulling $IMAGE (first run only)"; docker pull -q "$IMAGE" >/dev/null; }

# The image's karonte tree is not writable by the karonte user, so copy it
# somewhere writable before staging the firmware into it.
say "Karonte on $BINNAME (this takes a long time)"
docker run --rm -u karonte -v "$SRC/config:/cfg:ro" -v "$OUT:/out" "$IMAGE" bash -lc "
    source /home/karonte/.virtualenvs/karonte/bin/activate
    cd /home/karonte/karonte
    # The config's bin path is relative to the tree, which is read-only here.
    # Point it at the staged copy under /out instead of copying the whole tree:
    # the image ships router firmware samples that are not world-readable, so a
    # recursive copy fails partway and leaves tool/ missing.
    python -c \"
import json
c = json.load(open('/cfg/lk/$CONFIG'))
c['bin'] = ['/out/firmware/lk/$BINNAME']
json.dump(c, open('/out/run.json','w'))
\"
    python tool/karonte.py /out/run.json /out/karonte.log 2>&1 | tail -40
" | tee "$OUT/run.txt"
say "Output: $OUT"
