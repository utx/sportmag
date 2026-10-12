#!/usr/bin/env bash
# Build a book end to end:  build/book.sh <slug> [--kindle]
#   prep -> render graphics -> EPUB -> epubcheck (if EPUBCHECK_JAR is set) -> optional Kindle preview
set -euo pipefail
cd "$(dirname "$0")/.."
slug="${1:?usage: build/book.sh <slug> [--kindle]}"
python3 build/book.py prep "$slug"
node build/book-render.mjs "$slug"
python3 build/book.py epub "$slug"
if [ -n "${EPUBCHECK_JAR:-}" ]; then
  java -jar "$EPUBCHECK_JAR" -q "docs/books/$slug/$slug.epub" && echo "epubcheck: no errors"
fi
if [ "${2:-}" = "--kindle" ]; then
  node build/book-render.mjs "$slug" --kindle
fi
