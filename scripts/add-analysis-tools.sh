#!/usr/bin/env bash
# Add the bootloader analysis tools in tools/analysis_tools.json as submodules
# under analysis-tools/, grouped by category.
#
#   ./scripts/add-analysis-tools.sh [-y] [--dry-run] [--only NAME] [--full]
#
# Pointers only, same as oss-bootloaders: this records URLs and commits, it does
# not vendor code. Clones are shallow by default since these are tools to run
# rather than histories to mine; --full fetches complete history. The shallow
# flag is not written to .gitmodules, so other clones are unaffected.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

usage() { sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

DRY=0; ONLY=""; FULL=0; ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY=1 ;;
        --only) ONLY="$2"; shift ;;
        --full) FULL=1 ;;
        *) ARGS+=("$1") ;;
    esac
    shift
done
parse_common_args ${ARGS[@]+"${ARGS[@]}"}

MANIFEST="$TOOLS/analysis_tools.json"
[ -f "$MANIFEST" ] || die "missing $MANIFEST"

mapfile -t ENTRIES < <("$PYTHON" - "$MANIFEST" "$ONLY" <<'PY'
import json, sys
only = sys.argv[2]
for t in json.load(open(sys.argv[1])):
    if only and only != t["name"]: continue
    print(f'{t["category"]}\t{t["name"]}\t{t["clone"]}')
PY
)
[ ${#ENTRIES[@]} -eq 0 ] && die "no tools selected"

say "${#ENTRIES[@]} tool(s) to add under analysis-tools/"
for e in "${ENTRIES[@]}"; do
    IFS=$'\t' read -r cat name url <<< "$e"
    printf '    %-12s %-28s %s\n' "$cat" "$name" "$url"
done

[ "$DRY" = "1" ] && { say "--dry-run: nothing added"; exit 0; }
confirm "Add these as submodules of the BootBench superproject?" || { say "Nothing added."; exit 0; }

added=0; skipped=0; failed=()
for e in "${ENTRIES[@]}"; do
    IFS=$'\t' read -r cat name url <<< "$e"
    path="analysis-tools/$cat/$name"
    if [ -e "$ROOT/$path" ]; then
        say "$path already present, skipping"; skipped=$((skipped+1)); continue
    fi
    say "Adding $path"
    # Shallow by default: these are tools to run, not histories to mine, and a
    # full clone of codeql or angr is gigabytes. --full overrides.
    depth=(--depth 1); [ "$FULL" = "1" ] && depth=()
    if git -C "$ROOT" submodule add --quiet ${depth[@]+"${depth[@]}"} "$url" "$path" 2>/dev/null; then
        added=$((added+1))
    else
        warn "failed to add $name from $url"; failed+=("$name")
    fi
done

say "added $added, skipped $skipped, failed ${#failed[@]} ${failed[*]:-}"
[ "$added" = "0" ] && exit 0
cat <<EOF

  To publish:
    git add .gitmodules analysis-tools
    git commit -m "Add $added bootloader analysis tools as submodules"
EOF
