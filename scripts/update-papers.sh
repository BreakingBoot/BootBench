#!/usr/bin/env bash
# Re-run the literature search and regenerate PAPERS.md and papers.json.
#
#   ./scripts/update-papers.sh [--since YEAR] [--core-only]
#
# Writes into the BootBench superproject, not a submodule.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

usage() { sed -n '2,7p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }
parse_common_args "$@"

say "Searching dblp across the eight venues the SoK surveyed"
"$PYTHON" "$TOOLS/collect_papers.py" \
    --output "$ROOT/papers.json" --markdown "$ROOT/PAPERS.md" \
    ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}

say "Updated PAPERS.md and papers.json"
git -C "$ROOT" status --short PAPERS.md papers.json | sed 's/^/    /'
