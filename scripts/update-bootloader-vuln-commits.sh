#!/usr/bin/env bash
# Re-mine the bootloader git histories for vulnerability-fixing commits.
#
#   ./scripts/update-bootloader-vuln-commits.sh [-y] [--stage-only]
#
# Requires the nested bootloader submodules to be checked out; this is the
# expensive one, since it needs every bootloader's full history.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

usage() { sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

STAGE_ONLY=0; ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --stage-only) STAGE_ONLY=1 ;;
        *) ARGS+=("$1") ;;
    esac
    shift
done
parse_common_args ${ARGS[@]+"${ARGS[@]}"}

need_submodule oss-bootloaders
need_submodule bootloader_vuln_commits
STAGING="${STAGING:-${TMPDIR:-/tmp}/bootbench-commit-refresh}"

repair_empty_worktrees "$ROOT/oss-bootloaders"

repos=$(find "$ROOT/oss-bootloaders"/type[123] -mindepth 1 -maxdepth 1 -type d \
        -exec test -e '{}/.git' ';' -print 2>/dev/null | wc -l | tr -d ' ')
[ "$repos" = "0" ] && die "No bootloader submodules are checked out. Run:
    git -C oss-bootloaders submodule update --init --recursive"
say "$repos bootloader repositories are checked out"
[ "$repos" -lt 40 ] && warn "Fewer than the full corpus; the refresh will only cover what is present."

say "Staging the refresh in $STAGING/out (nothing written to the submodule yet)"
"$PYTHON" "$TOOLS/refresh_dataset.py" --root "$ROOT" --stage commits --staging "$STAGING/out"

[ "$STAGE_ONLY" = "1" ] && { say "--stage-only: stopping here. Staged data is in $STAGING/out"; exit 0; }

confirm "Apply this refresh to bootloader_vuln_commits?" || { say "Not applied."; exit 0; }

"$PYTHON" "$TOOLS/refresh_dataset.py" --root "$ROOT" --stage commits \
    --staging "$STAGING/out" --apply

report_submodule bootloader_vuln_commits
