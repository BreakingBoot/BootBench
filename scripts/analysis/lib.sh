#!/usr/bin/env bash
# Shared helpers for the analysis-tool runners.
set -euo pipefail

ANALYSIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$ANALYSIS_DIR/../.." && pwd)"
TOOLS="$ROOT/tools"
PYTHON="${PYTHON:-python3}"

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

need_docker() {
    command -v docker >/dev/null || die "docker is required for this runner"
    docker info >/dev/null 2>&1 || die "the docker daemon is not reachable"
}

# A daemon that cannot see a path silently produces nothing: the container
# writes into its own empty mount and exits 0. Check before doing real work.
check_mount() {
    local dir="$1" probe
    probe="$dir/.bootbench-mount-probe.$$"
    mkdir -p "$dir"
    if ! docker run --rm -v "$dir:/probe" alpine:3.20 \
            sh -c 'echo ok > /probe/'"$(basename "$probe")" >/dev/null 2>&1; then
        die "docker could not write to $dir"
    fi
    if [ ! -f "$probe" ]; then
        rm -f "$probe" 2>/dev/null || true
        die "the docker daemon cannot see $dir, so results would be lost silently.
    This usually means the daemon runs in a different mount namespace than the
    shell (a remote or rootless daemon, or a private tmpfs). Use a path inside
    the repository, for example --output $ROOT/analysis-results/..."
    fi
    rm -f "$probe"
}

# Resolve a bootloader name or path to an absolute source directory.
resolve_target() {
    local target="$1"
    if [ -d "$target" ]; then (cd "$target" && pwd); return; fi
    local hit
    hit=$(find "$ROOT/oss-bootloaders"/type[123] -mindepth 1 -maxdepth 1 -type d \
          -name "$target" 2>/dev/null | head -1)
    [ -n "$hit" ] || die "no such bootloader or directory: $target
    Try: ls $ROOT/oss-bootloaders/type*/"
    [ -e "$hit/.git" ] || die "$target is not checked out. Run:
    git -C oss-bootloaders submodule update --init ${hit#"$ROOT/oss-bootloaders/"}"
    echo "$hit"
}

# Look up a build recipe for a bootloader from tools/build_commands.json.
build_command_for() {
    "$PYTHON" - "$TOOLS/build_commands.json" "$1" <<'PY'
import json, sys, os
try:
    recipes = json.load(open(sys.argv[1]))
except OSError:
    sys.exit(0)
name = os.path.basename(sys.argv[2])
for r in recipes:
    if r["name"] == name:
        print(r.get("build", ""))
        break
PY
}

# Containers run as root, so anything they write into a bind mount comes back
# root-owned and the invoking user cannot delete their own results. Hand it
# back after each run.
reclaim_output() {
    local dir="$1"
    [ -d "$dir" ] || return 0
    find "$dir" -user root -print -quit 2>/dev/null | grep -q . || return 0
    docker run --rm -v "$dir:/reclaim" alpine:3.20 \
        chown -R "$(id -u):$(id -g)" /reclaim >/dev/null 2>&1 || \
        warn "could not reclaim ownership of $dir; files are root-owned"
}

build_image_if_needed() {  # <tag> <dockerfile>
    local tag="$1" dockerfile="$2"
    if docker image inspect "$tag" >/dev/null 2>&1; then return; fi
    say "Building $tag (first run only; this downloads a lot)"
    docker build -q -t "$tag" -f "$dockerfile" "$ANALYSIS_DIR/docker" >/dev/null
}
