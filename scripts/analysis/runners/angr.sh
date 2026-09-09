#!/usr/bin/env bash
# Load a compiled bootloader binary into angr and report a CFG summary.
#
#   run-tool.sh angr <binary> [--output DIR]
#
# angr is a framework, not a detector: this establishes that a given image
# loads and is analysable, which is the prerequisite for karonte, arbiter and
# BootStomp. Bootloader images are often raw blobs with no ELF headers, in
# which case pass --base and --arch.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

BIN=""; OUT=""; BASE=""; ARCH=""
while [ $# -gt 0 ]; do
    case "$1" in
        --output) OUT="$2"; shift ;;
        --base)   BASE="$2"; shift ;;
        --arch)   ARCH="$2"; shift ;;
        -h|--help) sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) BIN="$1" ;;
    esac
    shift
done
[ -n "$BIN" ] && [ -f "$BIN" ] || die "usage: run-tool.sh angr <binary>"
need_docker
BIN="$(cd "$(dirname "$BIN")" && pwd)/$(basename "$BIN")"
NAME="$(basename "$BIN")"
OUT="${OUT:-$ROOT/analysis-results/angr/$NAME}"; mkdir -p "$OUT"
check_mount "$OUT"

IMAGE=bootbench/pytools
build_image_if_needed "$IMAGE" "$ANALYSIS_DIR/docker/pytools.Dockerfile"

say "Loading $NAME into angr (first run installs angr; several minutes)"
docker run --rm -v "$BIN:/work/target:ro" -v "$OUT:/out" "$IMAGE" bash -eo pipefail -c "
    pip install --quiet angr >/dev/null 2>&1 || pip install angr
    python3 - <<'PY'
import json, angr, logging
logging.getLogger('angr').setLevel('ERROR')
logging.getLogger('cle').setLevel('ERROR')
opts = {}
$( [ -n "$BASE" ] && echo "opts['main_opts'] = {'base_addr': int('$BASE', 0)}" )
$( [ -n "$ARCH" ] && echo "opts['arch'] = '$ARCH'" )
p = angr.Project('/work/target', auto_load_libs=False, **opts)
cfg = p.analyses.CFGFast(normalize=True)
funcs = list(cfg.kb.functions.values())
summary = {
  'arch': str(p.arch.name), 'entry': hex(p.entry),
  'loader': str(p.loader.main_object),
  'functions': len(funcs),
  'blocks': sum(len(f.block_addrs_set) for f in funcs),
  'largest': sorted(((len(f.block_addrs_set), f.name) for f in funcs), reverse=True)[:15],
}
json.dump(summary, open('/out/cfg-summary.json','w'), indent=2)
print(f\"  arch={summary['arch']} entry={summary['entry']}\")
print(f\"  {summary['functions']} functions, {summary['blocks']} basic blocks\")
for n, name in summary['largest'][:8]:
    print(f'    {n:5d} blocks  {name}')
PY
"
reclaim_output "$OUT"
say "Summary: $OUT/cfg-summary.json"
