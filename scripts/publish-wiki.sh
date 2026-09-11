#!/usr/bin/env bash
# Publish the generated wiki to the GitHub wiki repository.
#
#   ./scripts/publish-wiki.sh [--dry-run]
#
# A GitHub wiki is a separate git repository -- <repo>.wiki.git -- not a folder
# in the main one, so wiki/ has to be pushed there explicitly.
#
# Before this works, twice over:
#   1. Settings -> General -> Features -> tick "Wikis"
#   2. Create one page in the web UI. The wiki repository does not exist until
#      a first page is saved, so cloning before that fails.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

usage() { sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }
DRY=0
for a in "$@"; do case "$a" in --dry-run) DRY=1 ;; -h|--help) usage; exit 0 ;; esac; done

ORIGIN="$(git -C "$ROOT" config --get remote.origin.url)"
WIKI_URL="${ORIGIN%.git}.wiki.git"
STAGING="${TMPDIR:-/tmp}/bootbench-wiki"

say "Generating flat pages (GitHub wiki pages are addressed by filename)"
rm -rf "$STAGING/pages"
"$PYTHON" "$TOOLS/generate_wiki.py" --root "$ROOT" --output "$STAGING/pages" --flat

say "Wiki repository: $WIKI_URL"
if [ ! -d "$STAGING/repo/.git" ]; then
    rm -rf "$STAGING/repo"
    if ! git clone --quiet "$WIKI_URL" "$STAGING/repo" 2>/dev/null; then
        die "could not clone $WIKI_URL

    The wiki repository does not exist yet. On GitHub:
      1. Settings -> General -> Features -> tick \"Wikis\"
      2. Open the Wiki tab and save any page, even an empty one
    Then run this again."
    fi
fi

git -C "$STAGING/repo" rm -q -r --ignore-unmatch . >/dev/null 2>&1 || true
cp "$STAGING/pages"/*.md "$STAGING/repo/"
# Figures live in a subdirectory. Only *pages* have to be flat in a GitHub
# wiki; files referenced by a page may be nested, and the markdown refers to
# them by the same relative path in both layouts.
rm -rf "$STAGING/repo/figures"
cp -r "$STAGING/pages/figures" "$STAGING/repo/figures"
git -C "$STAGING/repo" add -A

if git -C "$STAGING/repo" diff --cached --quiet; then
    say "no changes"; exit 0
fi
say "$(git -C "$STAGING/repo" diff --cached --numstat | wc -l) page(s) changed"
git -C "$STAGING/repo" diff --cached --name-status | head -15 | sed 's/^/    /'

if [ "$DRY" = "1" ]; then
    say "--dry-run: staged in $STAGING/repo, nothing pushed"
    exit 0
fi
confirm "Commit and push these to the wiki?" || { say "Not pushed."; exit 0; }
git -C "$STAGING/repo" commit -q -m "Update generated wiki"
git -C "$STAGING/repo" push
say "pushed to $WIKI_URL"
