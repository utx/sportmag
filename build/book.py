#!/usr/bin/env python3
"""Book builder: books/<slug>/ -> one Kindle-friendly EPUB.

    python3 build/book.py prep <slug>     # expand macros, write pages for Chromium to render
    node build/book-render.mjs <slug>     # cover + every graphic -> PNG
    python3 build/book.py epub <slug>     # assemble docs/books/<slug>/<slug>.epub

`build/book.sh <slug>` runs all three, then epubcheck and a Kindle-sized preview.

Source layout (books/<slug>/):
  book.json        title, subtitle, chapters [{file, title, kicker, dek}]
  cover.html       the cover, laid out at 800x1280 CSS px (rendered to 1600x2560)
  chapters/*.html  XHTML-safe fragments. Macros:
      <item name=".." icon="w-slug" tier="S|A|B|C|D" rarity=".." stats="Label=value;Label=value">..</item>
      <tierboard title=".."/>   tier board of every <item> in the chapter
      <div class="g" id="g-.." data-alt="..">hand-built graphic</div><!--/g-->
      <div class="pic"><img src="img/x.jpg" alt=".."/><p class="cap">..</p></div>
      <div class="box word"><h4>Word Watch</h4><dl><dt>..</dt><dd>..</dd></dl></div>  (feeds the word bank)
  img/, art/       Epic Games images (fan content policy) and our own art
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import shutil
import sys
import uuid
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "out" / "book"
DOCS = ROOT / "docs"
SITE_URL = "https://utx.github.io/sportmag/"

EPIC_DISCLAIMER = ("Portions of the materials used are trademarks and/or copyrighted works of Epic Games, Inc. "
                   "All rights reserved by Epic. This material is not official and is not endorsed by Epic.")

TIERS = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1}
TIER_NAMES = {"S": "Super", "A": "Awesome", "B": "Brilliant (sometimes)", "C": "Can work", "D": "Don't bother"}

JUG = ('<svg viewBox="0 0 40 52" class="jug{cls}"><path d="M8 14c0-4 3-6 6-7V2h12v5c3 1 6 3 6 7v30c0 3-2 5-5 5H13c-3 0'
       '-5-2-5-5z" /><path class="band" d="M8 24h24v8H8z"/><path class="h" d="M32 16c7 0 7 16 0 16" fill="none"/></svg>')


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load(slug: str) -> dict:
    d = ROOT / "books" / slug
    book = json.loads((d / "book.json").read_text(encoding="utf-8"))
    book["dir"] = d
    book["slug"] = slug
    for i, ch in enumerate(book["chapters"]):
        ch.setdefault("slug", slugify(Path(ch["file"]).stem.split("-", 1)[-1]))
        ch["n"] = i
    return book


def attrs(s: str) -> dict:
    return {k: html.unescape(v) for k, v in re.findall(r'([\w-]+)="([^"]*)"', s)}


def card_html(it: dict) -> str:
    n = TIERS[it["tier"]]
    jugs = "".join(JUG.format(cls="" if i < n else " empty") for i in range(5))
    art = (f'<img src="img/{it["icon"]}.png" alt=""/>' if it.get("icon")
           else '<div class="card__noart">COLLAB<br/>ITEM</div>')
    return (f'<div class="card t-{it["tier"]}"><div class="card__art">{art}</div>'
            f'<div class="card__tier"><small>TIER</small>{it["tier"]}</div><div class="card__jugs">{jugs}</div></div>')


def expand(book: dict, ch: dict, frag: str) -> tuple[str, list[dict]]:
    """Expand <item> and <tierboard/> macros. Returns html + the chapter's items."""
    items: list[dict] = []

    def item(m: re.Match) -> str:
        a = attrs(m.group(1))
        it = {"name": a["name"], "icon": a.get("icon", ""), "tier": a["tier"], "rarity": a.get("rarity", ""),
              "slug": slugify(a["name"]), "body": m.group(2).strip(), "stats": a.get("stats", ""), "short": a.get("short", a["name"])}
        if it["tier"] not in TIERS:
            raise SystemExit(f"{ch['file']}: bad tier for {it['name']}")
        if it["icon"] and not (book["dir"] / "img" / f"{it['icon']}.png").exists():
            raise SystemExit(f"{ch['file']}: missing icon img/{it['icon']}.png for {it['name']}")
        items.append(it)
        stats = ""
        if it["stats"]:
            pairs = [p.split("=", 1) for p in it["stats"].split(";") if p.strip()]
            stats = ('<table class="stats"><tr>' + "".join(f"<th>{html.escape(k.strip())}</th>" for k, _ in pairs) + "</tr><tr>"
                     + "".join(f"<td>{html.escape(v.strip())}</td>" for _, v in pairs) + "</tr></table>")
        n = TIERS[it["tier"]]
        rarity = f' · {html.escape(it["rarity"])}' if it["rarity"] else ""
        return (f'<div class="item" id="{it["slug"]}">\n'
                f'<div class="g g-card" id="g-card-{ch["slug"]}-{it["slug"]}" data-alt="{html.escape(it["name"])}, tier {it["tier"]}">'
                f'{card_html(it)}</div><!--/g-->\n'
                f'<h3>{html.escape(it["name"])}</h3>\n'
                f'<p class="verdict">Tier {it["tier"]} · {n}/5 Chug Jugs{rarity}</p>\n{stats}\n{it["body"]}\n</div>')

    s = re.sub(r"<item\s([^>]*)>(.*?)</item>", item, frag, flags=re.S)

    def board(m: re.Match) -> str:
        a = attrs(m.group(1))
        rows = []
        def chip(it: dict) -> str:
            art = f'<img src="img/{it["icon"]}.png" alt=""/>' if it["icon"] else '<div class="chip__no">?</div>'
            return f'<div class="chip">{art}<span>{html.escape(it["short"])}</span></div>'
        for t in TIERS:
            chips = "".join(chip(it) for it in items if it["tier"] == t)
            if chips:
                rows.append(f'<div class="trow t-{t}"><div class="trow__l">{t}</div><div class="trow__chips">{chips}</div></div>')
        alt = "; ".join(f"Tier {t}: " + ", ".join(it["name"] for it in items if it["tier"] == t)
                        for t in TIERS if any(it["tier"] == t for it in items))
        return (f'<div class="g g-board" id="g-board-{ch["slug"]}" data-alt="{html.escape(alt)}">'
                f'<div class="board"><div class="board__title">{html.escape(a.get("title", ch["title"]))}</div>'
                f'{"".join(rows)}</div></div><!--/g-->')

    s = re.sub(r"<tierboard\s*([^>]*?)/>", board, s)
    return s, items


def fragment(book: dict, ch: dict) -> tuple[str, list[dict]]:
    frag = (book["dir"] / "chapters" / ch["file"]).read_text(encoding="utf-8")
    return expand(book, ch, frag)


# --------------------------------------------------------------------------- prep (pages for Chromium)

def prep(slug: str) -> None:
    book = load(slug)
    out = OUT / slug
    (out / "pages").mkdir(parents=True, exist_ok=True)
    for f in (out / "pages").glob("*.html"):
        f.unlink()
    head = (f'<!doctype html><html><head><meta charset="utf-8"/><base href="/books/{slug}/"/>'
            '<link rel="stylesheet" href="/build/book/graphics.css"/></head><body>')
    jobs = []
    cover = (book["dir"] / "cover.html").read_text(encoding="utf-8")
    (out / "pages" / "cover.html").write_text(head + cover + "</body></html>", encoding="utf-8")
    jobs.append({"page": "cover.html", "ids": ["cover"]})
    for ch in book["chapters"]:
        if ch["file"].startswith("@"):
            continue
        body, _ = fragment(book, ch)
        ids = re.findall(r'<div class="g[^"]*" id="(g-[\w-]+)"', body)
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            raise SystemExit(f"{ch['file']}: duplicate graphic ids {dup}")
        name = f"{ch['slug']}.html"
        (out / "pages" / name).write_text(head + f'<div class="sheet">{body}</div></body></html>', encoding="utf-8")
        jobs.append({"page": name, "ids": ids})
    (out / "render.json").write_text(json.dumps(jobs, indent=1), encoding="utf-8")
    print(f"prep: {len(jobs)} pages, {sum(len(j['ids']) for j in jobs)} graphics")


# --------------------------------------------------------------------------- epub

EPUB_CSS = """
body { margin: 0; padding: 0; }
p { margin: 0 0 0.7em 0; text-indent: 0; }
h1, h2, h3, h4 { font-family: sans-serif; font-weight: bold; page-break-after: avoid; text-align: left; }
h1 { font-size: 1.75em; line-height: 1.15; margin: 0.2em 0 0.3em 0; }
h2 { font-size: 1.3em; line-height: 1.2; margin: 1.4em 0 0.4em 0; border-bottom: 2px solid #000; padding-bottom: 0.15em; }
h3 { font-size: 1.15em; margin: 0.3em 0 0.15em 0; }
h4 { font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.08em; margin: 0 0 0.35em 0; }
.kicker { font-family: sans-serif; font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.12em; margin: 0.4em 0 0 0; }
.dek { font-size: 1.05em; font-style: italic; margin: 0 0 1em 0; }
.fig { text-align: center; margin: 0.8em 0 1em 0; page-break-inside: avoid; }
.fig img { width: 100%; }
.fig-card { text-align: center; margin: 1.2em 0 0.3em 0; page-break-after: avoid; }
.fig-card img { width: 42%; }
.fig-opener img { width: 100%; }
.cap { font-size: 0.8em; font-style: italic; text-align: center; margin: 0.3em 0 0 0; }
.item { margin: 0 0 1.4em 0; padding: 0 0 0.6em 0; border-bottom: 1px solid #888; }
.item h3 { text-align: center; }
.verdict { font-family: sans-serif; font-weight: bold; text-align: center; font-size: 0.9em; margin: 0 0 0.5em 0; }
table.stats { width: 100%; border-collapse: collapse; margin: 0.2em 0 0.8em 0; font-size: 0.8em; }
table.stats th, table.stats td { border: 1px solid #000; padding: 0.2em 0.3em; text-align: center; }
table.stats th { font-family: sans-serif; font-weight: bold; }
table.data { width: 100%; border-collapse: collapse; margin: 0.5em 0 1em 0; font-size: 0.85em; }
table.data th, table.data td { border: 1px solid #000; padding: 0.25em 0.35em; text-align: left; vertical-align: top; }
table.data th { font-family: sans-serif; }
.box { border: 2px solid #000; padding: 0.5em 0.8em 0.3em 0.8em; margin: 1.1em 0; page-break-inside: avoid; }
.box-heavy { border-width: 4px; }
.word dl { margin: 0; }
.word dt { font-weight: bold; margin: 0.3em 0 0 0; }
.word dt small { font-weight: normal; font-style: italic; }
.word dd { margin: 0 0 0.4em 0; }
.ww { font-weight: bold; }
.tip { border-left: 5px solid #000; padding: 0.1em 0 0.1em 0.7em; margin: 0.6em 0 0.9em 0; }
.small { font-size: 0.85em; }
.center { text-align: center; }
.title-page { text-align: center; margin-top: 2em; }
.title-page h1 { text-align: center; font-size: 2.4em; }
.title-page .sub { font-size: 1.15em; font-style: italic; }
.toc { padding-left: 1.2em; }
.toc li { margin: 0 0 0.45em 0; }
ol.quiz > li { margin: 0 0 0.9em 0; }
ol.quiz ol { list-style-type: upper-alpha; margin: 0.2em 0 0 0; }
.cover-img { text-align: center; margin: 0; padding: 0; }
.cover-img img { max-width: 100%; }
"""


def xhtml(title: str, body: str, body_class: str = "") -> str:
    cls = f' class="{body_class}"' if body_class else ""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en-AU" xml:lang="en-AU">
<head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body{cls}>
{body}
</body>
</html>"""


def to_kindle_png(src: Path, dst: Path, max_w: int = 1200) -> None:
    """Greyscale, 16 levels (what an e-ink screen shows anyway): small files, crisp edges."""
    from PIL import Image, ImageOps
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg
    g = ImageOps.grayscale(im.convert("RGB"))
    if g.width > max_w:
        g = g.resize((max_w, round(g.height * max_w / g.width)), Image.LANCZOS)
    g = g.quantize(colors=16, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    g.save(dst, optimize=True)


def to_kindle_jpg(src: Path, dst: Path, max_side: int = 1200) -> None:
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(src))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg
    g = ImageOps.grayscale(im.convert("RGB"))
    g.thumbnail((max_side, max_side))
    g = ImageOps.autocontrast(g, cutoff=0.3)
    g.save(dst, quality=82, optimize=True)


def epubify(s: str, used_photos: set[str], rendered: Path) -> str:
    def swap(m: re.Match) -> str:
        cls, gid, rest = m.group(1), m.group(2), m.group(3)
        if not (rendered / f"{gid}.png").exists():
            raise SystemExit(f"epub: no rendered image for '{gid}'. Run build/book-render.mjs first.")
        alt = attrs(rest).get("data-alt", "")
        kind = "fig-card" if "g-card" in cls else ("fig fig-opener" if "g-opener" in cls else "fig")
        return f'<div class="{kind}"><img src="images/{gid}.png" alt="{html.escape(alt)}"/></div>'
    s = re.sub(r'<div class="(g[^"]*)" id="(g-[\w-]+)"([^>]*)>.*?</div><!--/g-->', swap, s, flags=re.S)

    def photo(m: re.Match) -> str:
        folder, stem = m.group(1), m.group(2)
        used_photos.add(f"{folder}/{stem}")
        return f'<img src="images/{folder}-{stem}.jpg"'
    s = re.sub(r'<img src="(img|art)/([\w-]+)\.(?:jpg|png)"', photo, s)
    s = re.sub(r'(<img [^>]*?)\s*/?>', lambda m: m.group(1).rstrip("/ ") + "/>", s)
    s = s.replace("<br>", "<br/>")
    s = re.sub(r"<dt>(.*?)\s*<small>(.*?)</small></dt>", r"<dt>\1 <small>(\2)</small></dt>", s)
    if "<svg" in s:
        raise SystemExit("epub: an inline <svg> survived outside a graphic block.")
    s = re.sub(r'\s(title|loading|aria-[\w-]+|data-[\w-]+)="[^"]*"', "", s)
    return s


def collect_words(frags: list[str]) -> list[tuple[str, str, str]]:
    words = {}
    for f in frags:
        for box in re.findall(r'<div class="box word[^"]*">(.*?)</div>', f, flags=re.S):
            for dt_, dd in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", box, flags=re.S):
                m = re.match(r"(.*?)<small>(.*?)</small>", dt_, flags=re.S)
                word, kind = (m.group(1).strip(), m.group(2).strip()) if m else (dt_.strip(), "")
                words.setdefault(re.sub(r"<[^>]+>", "", word).lower(), (re.sub(r"<[^>]+>", "", word), kind, dd.strip()))
    return [words[k] for k in sorted(words)]


def epub(slug: str) -> None:
    book = load(slug)
    rendered = OUT / slug / "g"
    if not (rendered / "cover.png").exists():
        raise SystemExit("epub: cover.png missing; run build/book-render.mjs first")
    work = OUT / slug / "epub"
    if work.exists():
        shutil.rmtree(work)
    (work / "images").mkdir(parents=True)

    used_photos: set[str] = set()
    frags, chapters = [], []
    raw = {}
    for ch in book["chapters"]:
        if not ch["file"].startswith("@"):
            raw[ch["file"]], _ = fragment(book, ch)
    words = collect_words(list(raw.values()))

    for i, ch in enumerate(book["chapters"]):
        if ch["file"] == "@glossary":
            dl = "".join(f'<dt>{html.escape(w)}{f"<small>{html.escape(k)}</small>" if k else ""}</dt><dd>{d}</dd>'
                         for w, k, d in words)
            frag = f'<p>{book.get("glossary_blurb", "")}</p>\n<div class="box word"><dl>{dl}</dl></div>'
        else:
            frag = raw[ch["file"]]
        num = ch.get("label", f"Chapter {ch['number']}" if "number" in ch else "")
        opener = ""
        m = re.search(r'<div class="g g-opener".*?<!--/g-->', frag, flags=re.S)
        if m:                                    # chapter art goes above the title
            opener, frag = m.group(0), frag.replace(m.group(0), "", 1)
        kicker = " · ".join(x for x in (num, ch.get("kicker", "")) if x)
        body = (f'<section epub:type="chapter">\n{opener}<p class="kicker">{html.escape(kicker)}</p>\n'
                f'<h1>{html.escape(ch["title"])}</h1>\n'
                + (f'<p class="dek">{ch["dek"]}</p>\n' if ch.get("dek") else "")
                + f'{frag}\n</section>')
        body = epubify(body, used_photos, rendered)
        name = f"c{i:02d}-{ch['slug']}.xhtml"
        doc = xhtml(ch["title"], body)
        try:
            ET.fromstring(doc.split("\n", 2)[2])
        except ET.ParseError as e:
            (work / name).write_text(doc, encoding="utf-8")
            raise SystemExit(f"epub: {name} is not well-formed: {e}\n  ({work / name})")
        (work / name).write_text(doc, encoding="utf-8")
        frags.append(body)
        chapters.append((name, ch))

    # images actually referenced
    gids = sorted(set(re.findall(r'src="images/(g-[\w-]+)\.png"', "".join(frags))))
    for gid in gids:
        to_kindle_png(rendered / f"{gid}.png", work / "images" / f"{gid}.png")
    for p in sorted(used_photos):
        folder, stem = p.split("/")
        src = next((book["dir"] / folder / f"{stem}{ext}" for ext in (".jpg", ".png") if (book["dir"] / folder / f"{stem}{ext}").exists()), None)
        if not src:
            raise SystemExit(f"epub: missing {p}.jpg/png")
        to_kindle_jpg(src, work / "images" / f"{folder}-{stem}.jpg")
    from PIL import Image
    cover = Image.open(rendered / "cover.png").convert("RGB")
    cover.thumbnail((1600, 2560))
    cover.save(work / "images" / "cover.jpg", quality=90, optimize=True)

    (work / "cover.xhtml").write_text(xhtml("Cover", f'<div class="cover-img"><img src="images/cover.jpg" alt="{html.escape(book["title"])} cover"/></div>'), encoding="utf-8")
    title_page = (f'<div class="title-page"><p class="kicker">{html.escape(book["series"])}</p>\n<h1>{html.escape(book["title"])}</h1>\n'
                  f'<p class="sub">{html.escape(book["subtitle"])}</p>\n<p class="small">{html.escape(book["version_note"])}</p>\n'
                  f'<p class="small">An unofficial Fortnite fan book.</p>\n<p class="small"><i>{EPIC_DISCLAIMER}</i></p></div>')
    (work / "title.xhtml").write_text(xhtml("Title page", title_page), encoding="utf-8")
    toc_items = "".join(f'<li><a href="{n}">{html.escape(ch["title"])}</a>'
                        + (f' <span class="small">({html.escape(ch["toc"])})</span>' if ch.get("toc") else "") + "</li>"
                        for n, ch in chapters)
    (work / "contents.xhtml").write_text(xhtml("Contents", f'<h1>Contents</h1>\n<ol class="toc">{toc_items}</ol>'), encoding="utf-8")
    nav = xhtml("Contents", '<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>'
                + "".join(f'<li><a href="{n}">{html.escape(ch["title"])}</a></li>' for n, ch in chapters)
                + '</ol></nav>\n<nav epub:type="landmarks" hidden="hidden"><ol>'
                + '<li><a epub:type="cover" href="cover.xhtml">Cover</a></li>'
                + '<li><a epub:type="toc" href="contents.xhtml">Contents</a></li>'
                + f'<li><a epub:type="bodymatter" href="{chapters[0][0]}">Start reading</a></li></ol></nav>')
    (work / "nav.xhtml").write_text(nav, encoding="utf-8")
    (work / "style.css").write_text(EPUB_CSS, encoding="utf-8")

    book_id = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, SITE_URL + 'books/' + slug)}"
    modified = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                '<item id="css" href="style.css" media-type="text/css"/>',
                '<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
                '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
                '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
                '<item id="contents" href="contents.xhtml" media-type="application/xhtml+xml"/>',
                '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>']
    for f in sorted((work / "images").iterdir()):
        if f.name == "cover.jpg":
            continue
        mt = "image/png" if f.suffix == ".png" else "image/jpeg"
        manifest.append(f'<item id="i-{f.stem}" href="images/{f.name}" media-type="{mt}"/>')
    manifest += [f'<item id="c{i}" href="{n}" media-type="application/xhtml+xml"/>' for i, (n, _) in enumerate(chapters)]
    spine = (['<itemref idref="cover" linear="yes"/>', '<itemref idref="title"/>', '<itemref idref="contents"/>']
             + [f'<itemref idref="c{i}"/>' for i in range(len(chapters))])
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en-AU">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{book_id}</dc:identifier>
    <dc:title>{html.escape(book['title'])}: {html.escape(book['subtitle'])}</dc:title>
    <dc:creator>The Chug Jug</dc:creator>
    <dc:publisher>The Chug Jug (unofficial fan publication)</dc:publisher>
    <dc:language>en-AU</dc:language>
    <dc:date>{book['date']}</dc:date>
    <dc:description>{html.escape(book['description'])}</dc:description>
    <dc:rights>{html.escape(EPIC_DISCLAIMER)}</dc:rights>
    <meta property="dcterms:modified">{modified}</meta>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
    {chr(10).join('    ' + m for m in manifest).strip()}
  </manifest>
  <spine toc="ncx">
    {' '.join(spine)}
  </spine>
</package>"""
    points = [("contents.xhtml", "Contents")] + [(n, ch["title"]) for n, ch in chapters]
    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head><meta name="dtb:uid" content="{book_id}"/></head>
<docTitle><text>{html.escape(book['title'])}</text></docTitle>
<navMap>{"".join(f'<navPoint id="np{i}" playOrder="{i + 1}"><navLabel><text>{html.escape(t)}</text></navLabel><content src="{n}"/></navPoint>' for i, (n, t) in enumerate(points))}</navMap>
</ncx>"""
    (work / "content.opf").write_text(opf, encoding="utf-8")
    (work / "toc.ncx").write_text(ncx, encoding="utf-8")

    home = DOCS / "books" / slug
    home.mkdir(parents=True, exist_ok=True)
    out = home / f"{slug}.epub"
    with zipfile.ZipFile(out, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>""", compress_type=zipfile.ZIP_DEFLATED)
        for f in sorted(work.rglob("*")):
            if f.is_file():
                z.write(f, "OEBPS/" + f.relative_to(work).as_posix(), compress_type=zipfile.ZIP_DEFLATED)
    shutil.copy(work / "images" / "cover.jpg", home / "cover.jpg")
    nwords = len(re.sub(r"<[^>]+>", " ", "".join(frags)).split())
    print(f"epub: {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB, {len(gids)} graphics, "
          f"{len(used_photos)} pictures, ~{nwords} words, {len(words)} glossary words)")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("prep", "epub"):
        raise SystemExit(__doc__)
    {"prep": prep, "epub": epub}[sys.argv[1]](sys.argv[2])
