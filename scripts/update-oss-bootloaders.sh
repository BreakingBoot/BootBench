#!/usr/bin/env bash
# Regenerate the bootloader inventory table and README in oss-bootloaders.
#
#   ./scripts/update-oss-bootloaders.sh [-y]
#
# Commit counts need the nested bootloader submodules checked out:
#   git -C oss-bootloaders submodule update --init --recursive
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

usage() { sed -n '2,8p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }
parse_common_args "$@"

need_submodule oss-bootloaders
SUB="$ROOT/oss-bootloaders"

repair_empty_worktrees "$ROOT/oss-bootloaders"

uninit=$(find "$SUB"/type[123] -mindepth 1 -maxdepth 1 -type d \
         '!' -exec test -e '{}/.git' ';' -print 2>/dev/null | wc -l | tr -d ' ')
if [ "$uninit" != "0" ]; then
    warn "$uninit bootloader submodule(s) are not checked out; their rows will say 'not initialized'."
    warn "For full commit data: git -C oss-bootloaders submodule update --init --recursive"
fi

say "Generating table.md"
"$PYTHON" "$TOOLS/generate_table.py" --root "$SUB" --output "$SUB/table.md"

# The retired CI concatenated description.md + table.md into README.md. That is
# destructive while description.md is a stub of empty headings: it would replace
# the curated bootloader list with a handful of blank sections. Only rebuild the
# README when there is actually prose to rebuild it from.
prose=$(grep -v '^#' "$SUB/description.md" 2>/dev/null | tr -d '[:space:]' | wc -c | tr -d ' ')
if [ "${prose:-0}" -eq 0 ]; then
    warn "description.md has no prose, only headings."
    warn "Leaving README.md alone -- concatenating it with table.md would replace"
    warn "the curated bootloader list with empty sections."
    say  "Wrote table.md only. Fill in description.md to have README.md rebuilt too."
else
    say "Rebuilding README.md from description.md + table.md"
    cat "$SUB/description.md" "$SUB/table.md" > "$SUB/README.md"
fi

report_submodule oss-bootloaders
