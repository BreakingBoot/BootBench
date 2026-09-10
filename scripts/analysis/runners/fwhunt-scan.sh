#!/usr/bin/env bash
# Analyse a UEFI module with FwHunt, or scan it against FwHunt rules.
#
#   run-tool.sh fwhunt-scan <module.efi> [--rules DIR] [--output DIR]
#
# Without --rules this runs FwHunt's analyser, which reports the protocols,
# GUIDs and services a module uses -- the attack-surface inventory for a single
# UEFI binary. With --rules it matches the module against a rule set
# (github.com/binarly-io/FwHunt).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

MOD=""; OUT=""; RULES=""
while [ $# -gt 0 ]; do
    case "$1" in
        --rules)  RULES="$2"; shift ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) MOD="$1" ;;
    esac
    shift
done
[ -n "$MOD" ] && [ -f "$MOD" ] || die "usage: run-tool.sh fwhunt-scan <module.efi>"
need_docker
MOD="$(cd "$(dirname "$MOD")" && pwd)/$(basename "$MOD")"
NAME="$(basename "$MOD")"
OUT="${OUT:-$ROOT/analysis-results/fwhunt-scan/$NAME}"; mkdir -p "$OUT"
check_mount "$OUT"
# A runner that die()s partway leaves root-owned output behind, which the
# invoking user then cannot delete. Reclaim on any exit, not just success.
trap 'reclaim_output "$OUT"' EXIT

IMAGE=bootbench/fwhunt
# fwhunt-scan needs rizin, which it builds from source. Its own Dockerfile
# already does that correctly, so use the checked-in submodule rather than
# maintaining a second recipe here.
FWHUNT_SRC="$ROOT/analysis-tools/static/fwhunt-scan"
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    [ -f "$FWHUNT_SRC/Dockerfile" ] || die "fwhunt-scan submodule not checked out. Run:
    git submodule update --init analysis-tools/static/fwhunt-scan"
    say "Building $IMAGE from the submodule's Dockerfile (builds rizin; slow, first run only)"
    docker build -q -t "$IMAGE" "$FWHUNT_SRC" >/dev/null
fi

if [ -n "$RULES" ]; then
    RULES="$(cd "$RULES" && pwd)"
    say "Scanning $NAME against rules in $(basename "$RULES")"
    for r in "$RULES"/*.yml "$RULES"/*.yaml; do
        [ -f "$r" ] || continue
        docker run --rm -v "$MOD:/work/module:ro" -v "$r:/rule.yml:ro" "$IMAGE" \
            scan-module --rule /rule.yml /work/module || true
    done | tee "$OUT/scan.txt"
else
    say "Analysing $NAME (protocols, GUIDs, services)"
    docker run --rm -v "$MOD:/work/module:ro" "$IMAGE" \
        analyze-module /work/module | tee "$OUT/analysis.txt"
fi
say "Output: $OUT"
