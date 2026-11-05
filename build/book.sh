#!/usr/bin/env bash
# Build a book end to end:  build/book.sh <slug> [--kindle]
#   prep -> render graphics -> EPUB -> epubcheck (if EPUBCHECK_JAR is set) -> optional Kindle preview
set -euo pipefail
cd "$(dirname "$0")/.."
slug="${1:?usage: build/book.sh <slug> [--kindle]}"
if [ -f "books/$slug/photos.json" ]; then python3 build/book_fetch.py "$slug"; fi
python3 build/book.py prep "$slug"
node build/book-render.mjs "$slug"
python3 build/book.py epub "$slug"
if [ -n "${EPUBCHECK_JAR:-}" ]; then
  epub="docs/books/$slug/$slug.epub"; [ -f "build/out/book/$slug/$slug.epub" ] && epub="build/out/book/$slug/$slug.epub"
  java -jar "$EPUBCHECK_JAR" -q "$epub" && echo "epubcheck: no errors"
fi
if [ "${2:-}" = "--kindle" ]; then
  node build/book-render.mjs "$slug" --kindle
fi
