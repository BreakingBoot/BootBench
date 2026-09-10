#!/usr/bin/env bash
# Run CodeQL over a bootloader's source.
#
#   run-tool.sh codeql <bootloader> [--queries SUITE] [--build "CMD"] [--output DIR]
#
# --queries takes a bare suite name (security-and-quality, security-extended,
# code-scanning) or a fully qualified pack path.
#
# Creates a CodeQL database by watching a real build, then runs a query suite
# over it and writes SARIF plus a CSV summary.
#
# C/C++ databases require the code to actually compile, which is the single
# biggest obstacle to running CodeQL on bootloaders: most need a cross
# toolchain. tools/build_commands.json holds a recipe per bootloader; pass
# --build to override. Everything runs in a container, so the host needs
# neither CodeQL nor a toolchain.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

TARGET=""; QUERIES="security-and-quality"; BUILD=""; OUT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --queries) QUERIES="$2"; shift ;;
        --build)   BUILD="$2"; shift ;;
        --output)  OUT="$2"; shift ;;
        -h|--help) sed -n '2,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) TARGET="$1" ;;
    esac
    shift
done
[ -n "$TARGET" ] || die "usage: run-tool.sh codeql <bootloader> [--build CMD]"

need_docker
SRC="$(resolve_target "$TARGET")"
NAME="$(basename "$SRC")"
OUT="${OUT:-$ROOT/analysis-results/codeql/$NAME}"
mkdir -p "$OUT"
check_mount "$OUT"
# A runner that die()s partway leaves root-owned output behind, which the
# invoking user then cannot delete. Reclaim on any exit, not just success.
trap 'reclaim_output "$OUT"' EXIT

if [ -z "$BUILD" ]; then
    BUILD="$(build_command_for "$NAME")"
    [ -n "$BUILD" ] || die "no build recipe for '$NAME'.
    Add one to tools/build_commands.json, or pass --build \"<command>\"."
    say "Build recipe from tools/build_commands.json: $BUILD"
fi

IMAGE=bootbench/codeql
build_image_if_needed "$IMAGE" "$ANALYSIS_DIR/docker/codeql.Dockerfile"

say "Creating CodeQL database for $NAME"
# /src is mounted read-only because the build must not touch the checkout;
# it is copied to a writable path inside the container first.
# Write the build command to a file rather than embedding it in the command
# string. A recipe containing quotes -- grub needs TARGET_CFLAGS="-no-pie
# -fno-PIE" -- otherwise collides with the quoting around codeql's --command
# and is silently truncated.
printf '%s\n' "$BUILD" > "$OUT/build.sh"

# /src is mounted read-only because the build must not touch the checkout;
# it is copied to a writable path inside the container first.
docker run --rm \
    -v "$SRC:/src:ro" -v "$OUT:/out" \
    -w /work "$IMAGE" bash -eo pipefail -c '
        mkdir -p /work/src && cp -a /src/. /work/src/ && cd /work/src
        codeql database create /out/db --language=cpp --overwrite \
              --command="bash /out/build.sh" 2>&1 | tail -40
    ' || die "database creation failed. The build did not run to completion;
    see the log above. Try a different --build command."

# A bare suite name is expanded to the scoped pack path CodeQL expects;
# anything containing a "/" is passed through untouched.
case "$QUERIES" in
    */*) SUITE="$QUERIES" ;;
    *)   SUITE="codeql/cpp-queries:codeql-suites/cpp-${QUERIES}.qls" ;;
esac

say "Analysing with $SUITE"
docker run --rm -v "$OUT:/out" "$IMAGE" bash -eo pipefail -c "
    codeql database analyze /out/db --format=sarif-latest \
        --output=/out/results.sarif --download '$SUITE' 2>&1 | tail -15
    codeql database analyze /out/db --format=csv \
        --output=/out/results.csv --download '$SUITE' >/dev/null 2>&1 || true
"

if [ -f "$OUT/results.sarif" ]; then
    "$PYTHON" - "$OUT/results.sarif" <<'PY'
import json, sys, collections
d = json.load(open(sys.argv[1]))
runs = d.get("runs", [])
results = [r for run in runs for r in run.get("results", [])]
print(f"\n  {len(results)} CodeQL result(s)")
for rule, n in collections.Counter(r.get("ruleId", "?") for r in results).most_common(15):
    print(f"    {n:4d}  {rule}")
PY
    say "SARIF: $OUT/results.sarif"
else
    warn "no SARIF produced"
fi
