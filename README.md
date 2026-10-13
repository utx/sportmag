# Touchline

A weekly football, sport and games magazine, published at **https://utx.github.io/sportmag/**,
with a one-tap "Send to Kindle" button.

## How it's put together

```
issues/NNN/          one folder per Touchline issue
chugjug/issues/NNN/  one folder per issue of The Chug Jug (Fortnite fan magazine)
  issue.json         running order, headlines, page numbers
  cover.html         the cover (HTML + inline SVG art)
  editor.html        welcome letter on the contents page
  NN-*.html          article bodies (inline SVG graphics inside .g[data-epub] blocks)
src/assets/          CSS, fonts (self-hosted, SIL OFL), JS, favicon
build/build.py       issues/ -> docs/ (website) and docs/issues/NNN/*.epub (Kindle)
build/render.mjs     renders the cover + every graphic to PNG with Chromium for the EPUB
build/build.sh       runs all three steps
kindle/              Google Apps Script that emails an issue to the Kindle (see SETUP.md)
books/<slug>/         stand-alone books (book.json, cover.html, chapters/, img/); build/book.sh <slug>
                     -> docs/books/<slug>/<slug>.epub (Tier Pressure; The Complete Guide to JDL Football in NSW)
docs/                the generated site that GitHub Pages serves — don't edit by hand
```

## Build

```
build/build.sh            # needs python3 + Pillow, node + playwright (Chromium)
build/build.sh --shots    # also saves page screenshots to build/out/shots/ for checking
```

## Writing conventions

- **Word Watch** boxes (`<aside class="box box--word side">` with `<dt>/<dd>`) feed the Word Bank automatically;
  highlight the word in the text with `<span class="ww">…</span>`.
- Graphics live in `<div class="g" data-epub="g-unique-id">…</div><!--/g-->` so the Kindle edition can swap in a
  greyscale PNG. Inline SVG anywhere else will fail the EPUB build.
- Fragments must be well-formed XHTML (close every tag, `<br/>`, no `&nbsp;`); the EPUB step checks this.
- `<div class="web-only">…</div><!--/web-only-->` and `<div class="epub-only">…</div><!--/epub-only-->` for edition-specific bits.

## Publishing on GitHub Pages

Settings → Pages → *Deploy from a branch* → `main` / `/docs`.
