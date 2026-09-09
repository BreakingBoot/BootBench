#!/usr/bin/env bash
# Grep the top four security conferences for papers matching keywords.
#
#   run-tool.sh top4grep <keyword>[,<keyword>...] [--build-db] [--output DIR]
#
# Note: tools/collect_papers.py covers the same dblp source across all eight
# venues the SoK surveyed, and needs no database build. This runner exists so
# the original can be reproduced.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"

KEYWORDS=""; OUT=""; BUILD_DB=0
while [ $# -gt 0 ]; do
    case "$1" in
        --build-db) BUILD_DB=1 ;;
        --output) OUT="$2"; shift ;;
        -h|--help) sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) KEYWORDS="$1" ;;
    esac
    shift
done
[ -n "$KEYWORDS" ] || KEYWORDS="bootloader"
need_docker
OUT="${OUT:-$ROOT/analysis-results/top4grep}"; mkdir -p "$OUT"; check_mount "$OUT"

SRC="$ROOT/analysis-tools/survey/top4grep"
[ -f "$SRC/setup.py" ] || die "top4grep submodule not checked out. Run:
    git submodule update --init analysis-tools/survey/top4grep"

IMAGE=bootbench/top4grep
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    say "Building $IMAGE (first run only)"
    docker build -q -t "$IMAGE" -f - "$SRC" >/dev/null <<'DOCKER'
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential \
 && rm -rf /var/lib/apt/lists/*
COPY . /src
RUN pip install --no-cache-dir -e /src
# top4grep tokenises titles with nltk, which needs its corpora downloaded.
RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt punkt_tab
WORKDIR /work
DOCKER
fi

# The shipped database is empty; --build-db populates it from dblp first.
say "Searching for: $KEYWORDS"
docker run --rm -v "$OUT:/out" "$IMAGE" bash -eo pipefail -c "
    $( [ "$BUILD_DB" = "1" ] && echo 'top4grep --build-db 2>&1 | tail -5;' )
    top4grep -k '$KEYWORDS' 2>&1
" | tee "$OUT/results.txt"
reclaim_output "$OUT"
say "Output: $OUT/results.txt"
