#!/usr/bin/env bash
# Shared helpers for the BootBench update scripts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS="$ROOT/tools"
PYTHON="${PYTHON:-python3}"

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

need_submodule() {
    local path="$1"
    [ -e "$ROOT/$path/.git" ] || die "$path is not checked out. Run: git submodule update --init $path"
}

# Ask before doing anything that writes into a submodule, unless --yes was given.
confirm() {
    [ "${ASSUME_YES:-0}" = "1" ] && return 0
    printf '\033[1;33m%s\033[0m [y/N] ' "$1"
    read -r reply < /dev/tty || return 1
    [[ "$reply" =~ ^[Yy]$ ]]
}

# Print what changed in a submodule and how to push it. Never commits.
report_submodule() {
    local path="$1"
    local changed
    changed="$(git -C "$ROOT/$path" status --porcelain | wc -l | tr -d ' ')"
    if [ "$changed" = "0" ]; then
        say "$path: no changes"
        return
    fi
    say "$path: $changed file(s) changed"
    git -C "$ROOT/$path" status --short | head -20 | sed 's/^/    /'
    [ "$changed" -gt 20 ] && echo "    ... and $((changed - 20)) more"
    cat <<EOF

  To publish:
    git -C $path add -A
    git -C $path commit -m "<message>"
    git -C $path push
    git add $path && git commit -m "Bump $path"
EOF
}

# `git submodule update --init` can leave a submodule cloned with HEAD set but
# no files checked out. Git then reports every tracked file as a staged
# deletion, and committing that would empty the repository. Detect and repair.
#
# Note: `git submodule status --recursive` is NOT usable for this. It recurses
# into each submodule and drops top-level entries whose worktree is empty --
# exactly the ones we are looking for. Use the non-recursive listing.
repair_empty_worktrees() {
    local parent="$1" repaired=0 path
    while read -r _ path _; do
        [ -n "$path" ] || continue
        [ -e "$parent/$path/.git" ] || continue
        # A populated checkout has tracked files; an empty worktree has none.
        [ -n "$(git -C "$parent/$path" ls-files 2>/dev/null | head -1)" ] && continue
        # --force resets to the recorded commit and checks the files out, which
        # also fixes a submodule sitting on the wrong commit.
        if git -C "$parent" submodule update --force --init "$path" >/dev/null 2>&1; then
            repaired=$((repaired + 1))
            say "repaired empty worktree: $path"
        else
            warn "could not repair $path"
        fi
    done < <(git -C "$parent" submodule status 2>/dev/null)
    [ "$repaired" -gt 0 ] && \
        warn "$repaired submodule(s) had been cloned without a checkout; repaired."
    return 0
}

# Container-written files come back root-owned. Give them back.
reclaim_ownership() {
    local dir="$1"
    [ -d "$dir" ] || return 0
    find "$dir" -user root -print -quit 2>/dev/null | grep -q . || return 0
    command -v docker >/dev/null || { warn "root-owned files in $dir and no docker to fix them"; return 0; }
    docker run --rm -v "$dir:/reclaim" alpine:3.20         chown -R "$(id -u):$(id -g)" /reclaim >/dev/null 2>&1         && say "reclaimed ownership of $dir"         || warn "could not reclaim ownership of $dir"
}

parse_common_args() {
    ASSUME_YES=0
    EXTRA_ARGS=()
    while [ $# -gt 0 ]; do
        case "$1" in
            -y|--yes) ASSUME_YES=1 ;;
            -h|--help) usage; exit 0 ;;
            *) EXTRA_ARGS+=("$1") ;;
        esac
        shift
    done
}
