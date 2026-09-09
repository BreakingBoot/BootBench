#!/usr/bin/env bash
# Emulate or fuzz a UEFI DXE driver with efi_fuzz.
#
#   run-tool.sh efi_fuzz [example] [--list] [--output DIR]
#
# efi_fuzz runs a DXE driver under Qiling with the boot services emulated.
# `run` executes the driver once and reports what it did, which is the useful
# smoke test; the project's own run.sh drives an AFL++ loop instead, which
# needs a corpus and does not terminate.
#
# It ships three worked examples with the modules and metadata included, so no
# firmware of your own is needed. The image applies
# patches/efi_fuzz-modernise.patch, without which it no longer builds.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

EXAMPLE="smram_arbitrary_write"; OUT=""; LIST=0
while [ $# -gt 0 ]; do
    case "$1" in
        --list) LIST=1 ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) EXAMPLE="$1" ;;
    esac
    shift
done
need_docker
SRC="$ROOT/analysis-tools/dynamic/efi_fuzz"
[ -f "$SRC/efi_fuzz.py" ] || die "efi_fuzz submodule not checked out. Run:
    git submodule update --init analysis-tools/dynamic/efi_fuzz"

if [ "$LIST" = "1" ]; then
    say "Bundled examples"
    for e in "$SRC"/examples/*/; do
        [ -d "$e" ] || continue
        printf "  %-24s %s\n" "$(basename "$e")" "$(ls "$e" | grep '\.efi$' | tr '\n' ' ')"
    done
    exit 0
fi
[ -d "$SRC/examples/$EXAMPLE" ] || die "no such example: $EXAMPLE
    List them with: run-tool.sh efi_fuzz --list"

OUT="${OUT:-$ROOT/analysis-results/efi_fuzz/$EXAMPLE}"; mkdir -p "$OUT"; check_mount "$OUT"

IMAGE=bootbench/efi_fuzz
# The Dockerfile copies only requirements.txt, so the source is mounted at run
# time. That means the patch has to reach the *runtime* tree as well as the
# build context -- patching only the build copy leaves the Qiling API fix out
# of the code that actually executes. Keep one patched checkout and use it for
# both.
PATCHED="$ROOT/analysis-results/.efi_fuzz-patched"
if [ ! -f "$PATCHED/.patched" ]; then
    say "staging a patched efi_fuzz checkout"
    rm -rf "$PATCHED"; mkdir -p "$PATCHED"
    cp -a "$SRC/." "$PATCHED/"; rm -rf "$PATCHED/.git"
    patch -s -p1 -d "$PATCHED" < "$ANALYSIS_DIR/patches/efi_fuzz-modernise.patch" \
        || die "could not apply efi_fuzz-modernise.patch"
    touch "$PATCHED/.patched"
    say "applied efi_fuzz-modernise.patch"
fi

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    say "Building $IMAGE (builds Triton and Capstone from source; slow, first run only)"
    docker build -q -t "$IMAGE" "$PATCHED" >/dev/null
fi

# The target module and its metadata json share a basename in each example.
TARGET=$(basename "$(ls "$SRC/examples/$EXAMPLE"/*.json | head -1)" .json)
say "efi_fuzz run on $EXAMPLE/$TARGET.efi"
docker run --rm -v "$PATCHED:/src:ro" -v "$OUT:/out" "$IMAGE" bash -c "
    cp -a /src /tmp/ef && cd /tmp/ef/examples/$EXAMPLE
    python3 ../../efi_fuzz.py run $TARGET.efi -j $TARGET.json 2>&1 | tail -40
" | tee "$OUT/run.txt"
reclaim_output "$OUT"
say "Output: $OUT/run.txt"
