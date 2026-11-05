#!/usr/bin/env python3
"""Download a book's photos from the source URLs recorded in its photos.json.

    python3 build/book_fetch.py <slug>

Some books (e.g. the LEGO book) keep their photos out of the public repo: books/<slug>/img/ is
git-ignored and this script rebuilds it. Each photos.json entry is one of:

  "img/x.jpg": {"source": "https://...", "credit": "...", ...}            one photo
  "img/x.jpg": {"composite": [{"src": "https://...", "label": "Name"}, ...], "credit": "..."}
                                                                          a labelled strip (minifigures)

Files that already exist are skipped. Downloads are polite (one at a time, browser-like UA).
"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
MAX_SIDE = 1400


def get(url: str) -> bytes:
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 - retry any network error
            if attempt == 3:
                raise SystemExit(f"fetch: {url}: {e}")
            time.sleep(2 ** attempt)
    raise AssertionError


def save_photo(data: bytes, dst: Path) -> None:
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg
    im = im.convert("RGB")
    im.thumbnail((MAX_SIDE, MAX_SIDE))
    im.save(dst, quality=88, optimize=True)


def strip(items: list[dict], dst: Path) -> None:
    """Minifigures side by side on white, name under each, wrapping after five."""
    from PIL import Image, ImageDraw, ImageFont
    cell_w, cell_h, label_h, per_row = 300, 360, 70, 5
    font_path = ROOT / "src" / "assets" / "fonts" / "barlow-condensed-latin-600-normal.woff2"
    try:
        font = ImageFont.truetype(str(font_path), 30)
    except OSError:
        font = ImageFont.load_default(size=28)
    n = len(items)
    cols = min(n, per_row)
    rows = (n + per_row - 1) // per_row
    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), "white")
    d = ImageDraw.Draw(sheet)
    for i, it in enumerate(items):
        im = Image.open(io.BytesIO(get(it["src"]))).convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg.convert("RGB")
        bbox = ImageOps_invert_bbox(im)
        if bbox:
            im = im.crop(bbox)
        im.thumbnail((cell_w - 30, cell_h - 20))
        r, c = divmod(i, per_row)
        row_n = min(per_row, n - r * per_row)
        x0 = (cols - row_n) * cell_w // 2 + c * cell_w
        y0 = r * (cell_h + label_h)
        sheet.paste(im, (x0 + (cell_w - im.width) // 2, y0 + cell_h - im.height - 6))
        label = it["label"]
        words, lines, line = label.split(), [], ""
        for w in words:
            test = (line + " " + w).strip()
            if d.textlength(test, font=font) > cell_w - 16 and line:
                lines.append(line)
                line = w
            else:
                line = test
        lines.append(line)
        for j, ln in enumerate(lines[:2]):
            tw = d.textlength(ln, font=font)
            d.text((x0 + (cell_w - tw) / 2, y0 + cell_h + 2 + j * 32), ln, fill="#111", font=font)
        time.sleep(0.3)
    sheet.save(dst, quality=88, optimize=True)


def ImageOps_invert_bbox(im):
    """Bounding box of everything that isn't (near) white."""
    from PIL import ImageOps
    g = ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 12 else 0)
    return g.getbbox()


def main(slug: str) -> None:
    d = ROOT / "books" / slug
    photos = json.loads((d / "photos.json").read_text(encoding="utf-8"))
    (d / "img").mkdir(exist_ok=True)
    got = skipped = 0
    for rel, meta in photos.items():
        dst = d / rel
        if dst.exists():
            skipped += 1
            continue
        if "composite" in meta:
            strip(meta["composite"], dst)
        elif "source" in meta:
            save_photo(get(meta["source"]), dst)
            time.sleep(0.5)
        else:
            continue
        got += 1
        print(f"  {rel}")
    print(f"fetch: {got} downloaded, {skipped} already there")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
