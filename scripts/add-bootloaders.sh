#!/usr/bin/env bash
# Add the bootloaders in tools/new_bootloaders.json to the oss-bootloaders
# submodule, under type1/ type2/ type3/.
#
#   ./scripts/add-bootloaders.sh [-y] [--dry-run] [--only NAME]
#
# Writes into the oss-bootloaders submodule. Nothing is committed; the script
# prints the commands to publish. Clones carry full history, because the corpus
# exists to be mined -- expect this to take a while.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

usage() { sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

DRY=0; ONLY=""; ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY=1 ;;
        --only) ONLY="$2"; shift ;;
        *) ARGS+=("$1") ;;
    esac
    shift
done
parse_common_args ${ARGS[@]+"${ARGS[@]}"}

need_submodule oss-bootloaders
SUB="$ROOT/oss-bootloaders"
MANIFEST="$TOOLS/new_bootloaders.json"
[ -f "$MANIFEST" ] || die "missing $MANIFEST"

mapfile -t ENTRIES < <("$PYTHON" - "$MANIFEST" "$ONLY" <<'PY'
import json, sys
only = sys.argv[2]
for b in json.load(open(sys.argv[1])):
    if only and only != b["name"]: continue
    print(f'{b["type"]}\t{b["name"]}\t{b["clone"]}')
PY
)
[ ${#ENTRIES[@]} -eq 0 ] && die "no bootloaders selected"

say "${#ENTRIES[@]} bootloader(s) to add to oss-bootloaders"
for e in "${ENTRIES[@]}"; do
    IFS=$'\t' read -r type name url <<< "$e"
    printf '    %-7s %-28s %s\n' "$type" "$name" "$url"
done

[ "$DRY" = "1" ] && { say "--dry-run: nothing added"; exit 0; }
confirm "Add these as submodules of oss-bootloaders?" || { say "Nothing added."; exit 0; }

added=0; skipped=0; failed=()
for e in "${ENTRIES[@]}"; do
    IFS=$'\t' read -r type name url <<< "$e"
    path="$type/$name"
    if [ -e "$SUB/$path" ]; then
        say "$path already present, skipping"; skipped=$((skipped+1)); continue
    fi
    say "Adding $path"
    # Full history, deliberately. These are mining targets -- a shallow clone
    # gives extract_vuln_commits.py one commit to look at.
    if git -C "$SUB" submodule add --quiet "$url" "$path" 2>/dev/null; then
        added=$((added+1))
    else
        warn "failed to add $name from $url"; failed+=("$name")
    fi
done

say "added $added, skipped $skipped, failed ${#failed[@]} ${failed[*]:-}"
[ "$added" = "0" ] && exit 0

say "Regenerating table.md"
"$PYTHON" "$TOOLS/generate_table.py" --root "$SUB" --output "$SUB/table.md" || true
report_submodule oss-bootloaders
