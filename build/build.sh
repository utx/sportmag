#!/usr/bin/env bash
# Build the whole site: HTML -> rendered graphics (Chromium) -> Kindle EPUB.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 build/build.py web
node build/render.mjs "$@"
python3 build/build.py epub
