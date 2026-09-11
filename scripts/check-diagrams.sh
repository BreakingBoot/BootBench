#!/usr/bin/env bash
# Render every Mermaid diagram in wiki/ to prove it parses.
#
# GitHub renders these blocks itself, so a syntax error shows up as a broken
# page rather than a build failure. This runs the real Mermaid renderer over
# every diagram so that cannot happen silently.
#
# Needs Docker. The image ships a Chrome that is missing from the layer, so
# PUPPETEER_EXECUTABLE_PATH is pointed at the system chromium instead, and the
# SVGs are written inside the container because the bind mount is not writable
# by the container's user.
set -euo pipefail

cd "$(dirname "$0")/.."
# shellcheck source=analysis/lib.sh
. "$(dirname "$0")/analysis/lib.sh"

IMAGE=minlag/mermaid-cli:latest
# Kept inside the repo: the Docker daemon here cannot see /tmp, and a mount it
# cannot see produces an empty result rather than an error.
WORK=$(mktemp -d "$PWD/.mermaid-check.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
# mktemp gives 0700; the container runs as a different user and must read these.
chmod 755 "$WORK"
check_mount "$WORK"

[ -d wiki ] || { echo "[error] wiki/ not generated -- run tools/generate_wiki.py first" >&2; exit 1; }
command -v docker >/dev/null || { echo "[error] docker not found" >&2; exit 1; }

python3 - "$WORK" <<'PY'
import pathlib, re, sys
out = pathlib.Path(sys.argv[1])
n = 0
for f in sorted(pathlib.Path("wiki").rglob("*.md")):
    for i, m in enumerate(re.finditer(r"```mermaid\n(.*?)```", f.read_text(), re.S)):
        name = f.relative_to("wiki").with_suffix("").as_posix().replace("/", "__")
        (out / f"{name}__{i}.mmd").write_text(m.group(1))
        n += 1
print(f"[INFO] extracted {n} diagrams")
PY

cat > "$WORK/run.sh" <<'INNER'
#!/bin/sh
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
echo '{"args":["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"]}' > /tmp/pp.json
mkdir -p /tmp/svg
fail=0; n=0
for f in /m/*.mmd; do
  n=$((n+1)); b=$(basename "$f" .mmd)
  if ! mmdc -p /tmp/pp.json -i "$f" -o "/tmp/svg/$b.svg" -q >/tmp/err 2>&1; then
    echo "[FAIL] $b"; grep -iE 'error|expect' /tmp/err | head -3; fail=1
  fi
done
echo "[INFO] $n diagrams, $(ls /tmp/svg | wc -l) rendered"
[ $fail -eq 0 ] && echo "[OK] all diagrams parse"
exit $fail
INNER
chmod 644 "$WORK"/*.mmd
chmod 755 "$WORK/run.sh"

docker run --rm -v "$WORK:/m" --entrypoint sh "$IMAGE" /m/run.sh \
  2>&1 | grep -viE 'generating single|deprecat|^$'
