#!/usr/bin/env bash
# Run one bootloader analysis tool against a target.
#
#   ./scripts/analysis/run-tool.sh <tool> <target> [tool args...]
#   ./scripts/analysis/run-tool.sh --list
#
# <target> is a bootloader name (resolved under oss-bootloaders/type*/), a
# source directory, or a firmware image, depending on what the tool consumes.
# Results land in analysis-results/<tool>/<target>/.
#
# Every runner works through docker, so the host needs no toolchain. Tools that
# need a commercial licence or physical hardware have no runner; --list says
# which, and tools/analysis_runners.json records why.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

MANIFEST="$TOOLS/analysis_runners.json"

list_tools() {
    "$PYTHON" - "$MANIFEST" <<'PY'
import json, sys, collections
tools = json.load(open(sys.argv[1]))
by = collections.defaultdict(list)
for t in tools:
    by[t["status"]].append(t)
labels = {"runnable": "Runnable here",
          "slow": "Runs, but no completed pass yet",
          "needs-image": "Runnable, but you supply a firmware image",
          "needs-license": "Needs commercial software",
          "needs-hardware": "Needs physical hardware or a specific target",
          "manual": "No runner: setup is bespoke"}
for status in ("runnable", "slow", "needs-image", "needs-license", "needs-hardware", "manual"):
    group = by.get(status)
    if not group:
        continue
    print(f"\n{labels[status]}")
    for t in sorted(group, key=lambda x: x["name"]):
        note = f"  -- {t['blocker']}" if t.get("blocker") else ""
        print(f"  {t['name']:24s} {t['input']:14s} {t['summary']}{note}")
print()
PY
}

[ $# -eq 0 ] && { sed -n '2,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; list_tools; exit 0; }
case "$1" in
    --list|-l) list_tools; exit 0 ;;
    -h|--help) sed -n '2,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
esac

TOOL="$1"; shift
RUNNER="$ANALYSIS_DIR/runners/$TOOL.sh"
if [ ! -x "$RUNNER" ]; then
    blocker=$("$PYTHON" - "$MANIFEST" "$TOOL" <<'PY'
import json, sys
for t in json.load(open(sys.argv[1])):
    if t["name"] == sys.argv[2]:
        print(t.get("blocker") or f"status: {t['status']}")
        break
PY
)
    if [ -n "$blocker" ]; then
        die "no runner for '$TOOL': $blocker
    See tools/analysis_runners.json, or ./scripts/analysis/run-tool.sh --list"
    fi
    die "unknown tool '$TOOL'. Try: ./scripts/analysis/run-tool.sh --list"
fi
exec "$RUNNER" "$@"
