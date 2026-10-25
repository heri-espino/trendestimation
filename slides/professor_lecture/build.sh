#!/usr/bin/env bash
set -euo pipefail
# bash slides/professor_lecture/build.sh [--html-only] [--skip-figures]
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$ROOT/../.." && pwd)"
HTML_ONLY=0
SKIP_FIGURES=0
for arg in "$@"; do
 case "$arg" in
  --html-only) HTML_ONLY=1 ;;
  --skip-figures) SKIP_FIGURES=1 ;;
  *) echo "Unknown option: $arg" >&2; exit 2 ;;
 esac
done
cd "$REPO"
if [ "$SKIP_FIGURES" -eq 0 ]; then
 python "$ROOT/make_figures.py"
fi
npx --yes @marp-team/marp-cli --theme-set "$ROOT/theme.css" \
 "$ROOT/main.md" --html --allow-local-files --output "$ROOT/main.html"
if [ "$HTML_ONLY" -eq 0 ]; then
 npx --yes @marp-team/marp-cli --theme-set "$ROOT/theme.css" \
  "$ROOT/main.md" --html --allow-local-files --pdf --output "$ROOT/main.pdf"
fi
echo "[lecture] HTML: $ROOT/main.html"
if [ "$HTML_ONLY" -eq 0 ]; then echo "[lecture] PDF: $ROOT/main.pdf"; fi
echo "[lecture] manifest: $ROOT/figures/manifest.json"
