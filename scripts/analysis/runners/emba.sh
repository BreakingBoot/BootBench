#!/usr/bin/env bash
# Run EMBA's firmware analysis battery over an image.
#
#   run-tool.sh emba <firmware> [--profile NAME] [--output DIR]
#
# EMBA orchestrates extraction plus a large number of checks (binary hardening,
# known CVEs, credentials, kernel config). It ships a prebuilt image, so no
# installer run is needed here.
#
# It wants --privileged for its mount-based extraction modules. That is a real
# privilege grant to a third-party container; it is passed because several
# modules silently do nothing without it, but run it on firmware you trust.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

IMG=""; OUT=""; PROFILE="default-scan"
while [ $# -gt 0 ]; do
    case "$1" in
        --profile) PROFILE="$2"; shift ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) IMG="$1" ;;
    esac
    shift
done
[ -n "$IMG" ] && [ -f "$IMG" ] || die "usage: run-tool.sh emba <firmware>"
need_docker
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"
FWDIR="$(dirname "$IMG")"; NAME="$(basename "$IMG")"
OUT="${OUT:-$ROOT/analysis-results/emba/$NAME}"; rm -rf "$OUT"; mkdir -p "$OUT"; check_mount "$OUT"

SRC="$ROOT/analysis-tools/dynamic/emba"
[ -f "$SRC/emba" ] || die "emba submodule not checked out. Run:
    git submodule update --init analysis-tools/dynamic/emba"
[ -f "$SRC/scan-profiles/$PROFILE.emba" ] || die "no such profile: $PROFILE
    Available: $(ls "$SRC/scan-profiles" | sed 's/\.emba$//' | tr '\n' ' ')"

# Without a populated CVE-search SQLite database emba refuses to start. Its
# own CI marks that as expected with config/gh_action, which skips the check;
# the NVD JSON feeds the installer fetched still drive the CVE modules.
[ -f "$SRC/config/gh_action" ] || { : > "$SRC/config/gh_action"; say "created config/gh_action (skips the CVE-search DB check)"; }

if [ ! -d "$SRC/external/emba_venv" ]; then
    die "emba's external/ tree is not populated, so every dependency check will fail.
    Run its installer once (about 4 GB):
      docker build -t bootbench/emba-installer - <<'EOF'
      FROM embeddedanalyzer/emba:2.0.3c
      RUN apt-get update && apt-get install -y --no-install-recommends docker.io
      EOF
      docker run --rm --privileged --pid=host \\
          -v \"$SRC:/emba\" -v /var/run/docker.sock:/var/run/docker.sock \\
          bootbench/emba-installer -c 'yes | ./installer.sh -g -f'
    --pid=host is needed because the installer checks for dockerd with pgrep."
fi

IMAGE=embeddedanalyzer/emba:2.0.3c
docker image inspect "$IMAGE" >/dev/null 2>&1 || { say "Pulling $IMAGE (large, first run only)"; docker pull -q "$IMAGE" >/dev/null; }

say "EMBA $PROFILE on $NAME"
# -i is emba's internal "already inside the container" flag: without it emba
# tries to modprobe ufs/nandsim/ubi/nbd on what it thinks is the host, fails,
# and aborts the dependency check.
#
# The image ships an empty /emba and expects the source mounted there. That
# only works once `installer.sh -g -f` has populated the checkout's external/
# tree (~4 GB); without it every dependency check fails. See PATCHES.md.
docker run --rm --privileged \
    -v "$FWDIR:/firmware:ro" -v "$OUT:/logs" -v "$SRC:/emba" \
    "$IMAGE" -c "./emba -i -l /logs -f /firmware/$NAME -p ./scan-profiles/$PROFILE.emba -y" \
    2>&1 | tail -40 | tee "$OUT/run.txt"
reclaim_output "$OUT"
[ -f "$OUT/html-report/index.html" ] && say "HTML report: $OUT/html-report/index.html"
say "Output: $OUT"
