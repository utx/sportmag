#!/usr/bin/env python3
"""Magazine builder for Touchline and The Chug Jug.

    python3 build/build.py web     # issues/* and chugjug/issues/*  ->  docs/  (the GitHub Pages site)
    python3 build/build.py epub    # docs/ + rendered graphics  ->  one Kindle .epub per issue

`build/build.sh` runs web -> render (Chromium screenshots of every graphic) -> epub.
Only the standard library and Pillow are needed.
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
SRC = ROOT / "src"
DOCS = ROOT / "docs"
RENDER_OUT = ROOT / "build" / "out"   # PNGs from render.mjs (git-ignored)

SITE_URL = "https://utx.github.io/sportmag/"

EPIC_DISCLAIMER = ("Portions of the materials used are trademarks and/or copyrighted works of Epic Games, Inc. "
                   "All rights reserved by Epic. This material is not official and is not endorsed by Epic.")

# Each magazine: where its issues live, where it publishes inside docs/, and its branding.
MAGS = {
    "touchline": {
        "src": ROOT / "issues", "path": "", "title": "Touchline", "epub": "touchline", "kindle_prefix": "",
        "logo": "TOUCH<span>LINE</span>", "body_class": "", "theme_color": "#151515",
        "tagline": "Football, sport &amp; games — for readers who like big matches and bigger words.",
        "small": "Facts were checked against match reports and official sources as we went to press. "
                 "Opinions are ours, and yes, we know which team we support.",
        "glossary_blurb": "Try using three of them in a sentence this week — bonus points if one of the sentences is about Manchester United.",
        "disclaimer": "",
        "sister": ("The Chug Jug", "chugjug/"),
    },
    "chugjug": {
        "src": ROOT / "chugjug" / "issues", "path": "chugjug/", "title": "The Chug Jug", "epub": "chugjug", "kindle_prefix": "cj",
        "logo": "THE CHUG <span>JUG</span>", "body_class": "mag-chugjug", "theme_color": "#1d1257",
        "tagline": "An unofficial Fortnite fan magazine. Fully topped up on everything new.",
        "small": "Made by fans, for fans. Facts checked against patch notes and the game's own data as we went to press; "
                 "the ratings are just our opinion. Always ask a grown-up before spending V-Bucks.",
        "glossary_blurb": "Drop three of them into conversation this week. Extra respect if you use one in the lobby.",
        "disclaimer": EPIC_DISCLAIMER,
        "sister": ("Touchline", ""),
    },
}

KINDLE_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2.5" width="14" height="19" rx="2"/>'
    '<path d="M8.5 7h7M8.5 10.5h7M8.5 14h4.5"/></svg>'
)

SECTION_STYLE = {"red": "", "sky": " a-kicker__sec--sky", "ink": " a-kicker__sec--ink", "grass": " a-kicker__sec--grass",
                 "common": " rarity--common", "uncommon": " rarity--uncommon", "rare": " rarity--rare",
                 "epic": " rarity--epic", "legendary": " rarity--legendary", "mythic": " rarity--mythic"}


# --------------------------------------------------------------------------- helpers
def load_issues(mag_key: str) -> list[dict]:
    mag = dict(MAGS[mag_key], key=mag_key)
    issues = []
    for d in sorted(p for p in mag["src"].iterdir() if p.is_dir()):
        meta = json.loads((d / "issue.json").read_text(encoding="utf-8"))
        meta["dir"] = d
        meta["mag"] = mag
        issues.append(meta)
    return issues


def up(path: str) -> str:
    """'chugjug/' -> '../' : how to climb out of a magazine folder back to docs/."""
    return "../" * path.count("/")


LICENCE_URLS = {
    "CC0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC BY 2.0": "https://creativecommons.org/licenses/by/2.0/",
    "CC BY 3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC BY-SA 2.0": "https://creativecommons.org/licenses/by-sa/2.0/",
    "CC BY-SA 3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
    "CC BY-SA 3.0 DE": "https://creativecommons.org/licenses/by-sa/3.0/de/deed.en",
    "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
}


def photo_credits(issue: dict) -> dict[str, str]:
    """photos.json -> {id: credit HTML}. Every photo is from Wikimedia Commons under a free licence."""
    f = issue["dir"] / "photos.json"
    if not f.exists():
        return {}
    out = {}
    for pid, m in json.loads(f.read_text(encoding="utf-8")).items():
        if "credit" in m:                      # e.g. in-game images: "Image: Epic Games / Fortnite"
            out[pid] = html.escape(m["credit"])
            continue
        page = "https://commons.wikimedia.org/wiki/File:" + m["file"].replace(" ", "_")
        lic = m["license"]
        out[pid] = (f'Photo: <a href="{html.escape(page)}">{html.escape(m["author"])}</a> / '
                    f'<a href="{LICENCE_URLS[lic]}">{lic}</a>, via Wikimedia Commons')
    return out


def read_fragment(issue: dict, name: str) -> str:
    s = (issue["dir"] / name).read_text(encoding="utf-8")
    credits = issue.setdefault("_credits", photo_credits(issue))
    def credit(m: re.Match) -> str:
        if m.group(1) not in credits:
            raise SystemExit(f"{name}: no photos.json entry for photo '{m.group(1)}'")
        return credits[m.group(1)]
    s = re.sub(r"@@([\w-]+)", credit, s)
    for src in re.findall(r'<img src="img/([\w-]+\.(?:jpg|png))"', s) + re.findall(r'href="img/([\w-]+\.(?:jpg|png))"', s):
        if not (issue["dir"] / "img" / src).exists():
            raise SystemExit(f"{name}: missing photo issues/{issue['slug']}/img/{src}")
    return s


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def collect_words(fragment: str) -> list[tuple[str, str, str]]:
    """Pull (word, part-of-speech, definition) out of every Word Watch box."""
    words = []
    for box in re.findall(r'<aside class="box box--word[^"]*">(.*?)</aside>', fragment, re.S):
        for dt_html, dd_html in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", box, re.S):
            m = re.match(r"(.*?)<small>(.*?)</small>", dt_html, re.S)
            word, pos = (m.group(1), m.group(2)) if m else (dt_html, "")
            words.append((strip_tags(word).strip(), strip_tags(pos).strip(), dd_html.strip()))
    return words


def page_shell(*, title: str, desc: str, body: str, issue: dict, rel: str, og_image: str | None = None,
               extra_head: str = "", body_class: str = "") -> str:
    """rel = path from this page back to docs/ root (e.g. '../../')."""
    mag = issue["mag"]
    base = rel + mag["path"]                     # this magazine's home folder
    og = f'<meta property="og:image" content="{SITE_URL}{mag["path"]}{og_image}">' if og_image else ""
    epub_href = f"{base}issues/{issue['slug']}/{mag['epub']}-{issue['slug']}.epub"
    disclaimer = f'<div class="small disclaimer">{mag["disclaimer"]}</div>' if mag["disclaimer"] else ""
    body_class = " ".join(c for c in (body_class, mag["body_class"]) if c)
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
{og}
<meta name="theme-color" content="{mag['theme_color']}">
<link rel="icon" href="{rel}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{rel}assets/fonts/anton-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/css/touchline.css">
{extra_head}
</head>
<body class="{body_class}" data-issue="{mag['kindle_prefix']}{issue['slug']}" data-epub="{epub_href}">
<header class="topbar">
  <div class="topbar__inner">
    <a class="topbar__logo" href="{base}issues/{issue['slug']}/index.html">{mag['logo']}</a>
    <span class="topbar__issue">Issue {issue['number']} · {html.escape(issue['date_display'])}</span>
    <span class="topbar__spacer"></span>
    <a class="topbar__link" href="{base}archive.html">Back issues</a>
    <button class="kindle-btn" type="button" data-kindle>{KINDLE_ICON}<span>Send<span class="kindle-btn__long"> to Kindle</span></span></button>
  </div>
</header>
<main>
{body}
</main>
<footer class="foot">
  <div class="foot__inner">
    <div class="foot__logo">{mag['logo']}</div>
    <div>{mag['tagline']}</div>
    <div>Issue {issue['number']} · {html.escape(issue['date_display'])} · <a href="{epub_href}">Download the Kindle edition</a> · <a href="{base}archive.html">All issues</a></div>
    <div class="small">{mag['small']}</div>
    <div>Also from us: <a href="{rel}{mag['sister'][1]}index.html">{mag['sister'][0]}</a></div>
    {disclaimer}
  </div>
</footer>
<div class="toast" role="status" aria-live="polite"></div>
<script src="{rel}assets/js/config.js"></script>
<script src="{rel}assets/js/touchline.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- web
def build_article_page(issue: dict, idx: int, glossary_html: str) -> str:
    arts = issue["articles"]
    a = arts[idx]
    if a["file"] == "@glossary":
        body_html = glossary_html
    else:
        body_html = read_fragment(issue, a["file"])
    body_html = re.sub(r'<div class="epub-only">.*?</div><!--/epub-only-->', "", body_html, flags=re.S)

    sec_cls = SECTION_STYLE.get(a.get("style", "red"), "")
    prev_link = (f'<a class="prev" href="{arts[idx-1]["slug"]}.html"><small>← Previous</small>'
                 f'<span>{arts[idx-1]["toc_title"]}</span></a>') if idx > 0 else \
                '<a class="prev" href="index.html"><small>← Cover</small><span>Contents</span></a>'
    next_link = (f'<a class="next" href="{arts[idx+1]["slug"]}.html"><small>Turn the page →</small>'
                 f'<span>{arts[idx+1]["toc_title"]}</span></a>') if idx + 1 < len(arts) else \
                '<a class="next" href="index.html"><small>The end →</small><span>Back to the cover</span></a>'

    body = f"""
<article class="article">
  <header class="a-hero">
    <div class="a-kicker"><span class="a-kicker__sec{sec_cls}">{a['section']}</span><span class="a-kicker__page">p.{a['page']}</span></div>
    <h1 class="a-title">{a['title_html']}</h1>
    <p class="a-dek">{a['dek']}</p>
    <div class="a-byline">{a['byline']}</div>
  </header>
  <div class="a-body">
{body_html}
  <div class="clear"></div>
  </div>
  <nav class="turner" aria-label="Page turner">{prev_link}{next_link}</nav>
</article>"""
    title = f"{strip_tags(a['title_html'])} — {issue['mag']['title']} Issue {issue['number']}"
    return page_shell(title=title, desc=strip_tags(a["dek"]), body=body, issue=issue, rel="../../" + up(issue["mag"]["path"]),
                      og_image=f"issues/{issue['slug']}/cover.png")


def build_issue_index(issue: dict, rel: str, link_prefix: str = "") -> str:
    """link_prefix is prepended to article links (the site root page lives outside the issue folder)."""
    cover = read_fragment(issue, issue["cover"])
    if link_prefix:                       # the magazine's home page sits outside the issue folder
        cover = re.sub(r'(src|href)="img/', rf'\1="{link_prefix}img/', cover)
    toc = []
    for i, a in enumerate(issue["articles"]):
        toc.append(f"""<a class="toc-item" href="{link_prefix}{a['slug']}.html">
  <span class="toc-item__num">{a['page']:02d}</span>
  <span><span class="toc-item__sec">{a['section']}</span>
  <span class="toc-item__title">{a['toc_title']}</span>
  <span class="toc-item__dek">{a.get('toc_dek', strip_tags(a['dek']))}</span></span>
</a>""")
    letter = read_fragment(issue, issue["editor_letter"]) if issue.get("editor_letter") else ""
    first = issue["articles"][0]["slug"]
    body = f"""
<section class="cover-wrap" aria-label="Cover">
{cover}
</section>
<div class="cover-actions">
  <a class="btn-ghost" href="{link_prefix}{first}.html">Start reading →</a>
  <button class="kindle-btn kindle-btn--big" type="button" data-kindle>{KINDLE_ICON}<span>Send this issue to Kindle</span></button>
</div>
<section class="contents" id="contents">
  <div class="contents__head"><h2>Inside</h2><p>Issue {issue['number']} · {html.escape(issue['date_display'])}</p></div>
  <div class="contents__grid">
{''.join(toc)}
  </div>
</section>
{letter}
"""
    title = f"{issue['mag']['title']} — Issue {issue['number']}: {issue['cover_headline']}"
    return page_shell(title=title, desc=issue["description"], body=body, issue=issue, rel=rel,
                      og_image=f"issues/{issue['slug']}/cover.png", body_class="is-cover")


def build_glossary(issue: dict) -> str:
    entries = []
    for a in issue["articles"]:
        if a["file"].startswith("@"):
            continue
        for word, pos, defn in collect_words(read_fragment(issue, a["file"])):
            entries.append((word, pos, defn, a))
    entries.sort(key=lambda e: e[0].lower())
    rows = "\n".join(
        f'<div><dt>{html.escape(w)}<small>{html.escape(p)}</small></dt><dd>{d} '
        f'<a href="{a["slug"]}.html">p.{a["page"]}</a></dd></div>'
        for w, p, d, a in entries)
    return f"""<p>Every word from this issue's <strong>Word Watch</strong> boxes, in one place. {issue['mag']['glossary_blurb']}</p>
<dl class="glossary wide">
{rows}
</dl>
<p class="muted small">{len(entries)} words this issue.</p>"""


def build_archive(issues: list[dict]) -> str:
    items = "".join(
        f"""<a class="archive__item" href="issues/{i['slug']}/index.html">
  <img src="issues/{i['slug']}/cover.png" alt="Cover of {i['mag']['title']} issue {i['number']}" loading="lazy" width="600" height="800">
  <b>Issue {i['number']}</b><span>{html.escape(i['date_display'])}</span></a>"""
        for i in reversed(issues))
    body = f"""<section class="archive"><h1>Back issues</h1><div class="archive__grid">{items}</div></section>"""
    mag = issues[-1]["mag"]
    return page_shell(title=f"{mag['title']} — Back issues", desc=f"Every issue of {mag['title']}.", body=body,
                      issue=issues[-1], rel=up(mag["path"]))


def build_web() -> None:
    DOCS.mkdir(exist_ok=True)
    if (DOCS / "assets").exists():
        shutil.rmtree(DOCS / "assets")
    shutil.copytree(SRC / "assets", DOCS / "assets")
    (DOCS / ".nojekyll").write_text("")
    render_jobs = []
    for key, mag in MAGS.items():
        if not mag["src"].exists():
            continue
        issues = load_issues(key)
        home = DOCS / mag["path"] if mag["path"] else DOCS
        for issue in issues:
            out = home / "issues" / issue["slug"]
            out.mkdir(parents=True, exist_ok=True)
            for f in out.glob("*.html"):
                f.unlink()
            glossary_html = build_glossary(issue)
            (out / "index.html").write_text(build_issue_index(issue, rel="../../" + up(mag["path"])), encoding="utf-8")
            for i, a in enumerate(issue["articles"]):
                (out / f"{a['slug']}.html").write_text(build_article_page(issue, i, glossary_html), encoding="utf-8")
            img_dir = issue["dir"] / "img"
            if img_dir.exists():
                shutil.copytree(img_dir, out / "img", dirs_exist_ok=True)
            render_jobs.append({"mag": key, "slug": issue["slug"], "page_dir": f"{mag['path']}issues/{issue['slug']}"})
        latest = issues[-1]
        (home / "index.html").write_text(
            build_issue_index(latest, rel=up(mag["path"]), link_prefix=f"issues/{latest['slug']}/"), encoding="utf-8")
        (home / "archive.html").write_text(build_archive(issues), encoding="utf-8")
        print(f"web: {mag['title']}: {len(issues)} issue(s) -> docs/{mag['path']}")
    (DOCS / "render.json").write_text(json.dumps(render_jobs, indent=2))
    stale = DOCS / "issues.json"
    if stale.exists():
        stale.unlink()


# --------------------------------------------------------------------------- epub
EPUB_CSS = """
body { font-family: serif; line-height: 1.5; margin: 0 4%; }
h1 { font-size: 1.9em; line-height: 1.1; margin: 0.4em 0 0.2em; text-transform: uppercase; }
h3 { font-size: 1.3em; margin: 1.4em 0 0.3em; text-transform: uppercase; }
h4 { font-size: 1.05em; margin: 1.2em 0 0.3em; text-transform: uppercase; letter-spacing: 0.05em; }
h5 { font-size: 1em; margin: 0.8em 0 0.2em; }
.kicker { font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.1em; margin: 1em 0 0; }
.dek { font-size: 1.1em; font-style: italic; margin: 0.3em 0 0.6em; }
.byline { font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.08em; border-bottom: 1px solid #000; padding-bottom: 0.5em; margin-bottom: 1em; }
p { margin: 0 0 0.8em; text-indent: 0; }
.ww { font-weight: bold; }
.box, aside { border: 1px solid #000; padding: 0.4em 0.8em; margin: 1em 0; }
.box--ink { border-width: 3px; }
dt { font-weight: bold; margin-top: 0.4em; }
dd { margin: 0 0 0.2em 0; }
.pull { border-top: 3px solid #000; border-bottom: 1px solid #000; margin: 1em 0; padding: 0.4em 0; }
.pull p { font-size: 1.25em; font-weight: bold; margin: 0 0 0.3em; }
cite { font-style: normal; font-size: 0.85em; text-transform: uppercase; }
figure { margin: 1em 0; text-align: center; }
figure img { width: 100%; }
figcaption { font-size: 0.85em; text-align: left; margin-top: 0.3em; }
table { border-collapse: collapse; width: 100%; font-size: 0.85em; margin: 0.6em 0 1em; }
caption { font-weight: bold; text-align: left; padding-bottom: 0.3em; }
th, td { border-bottom: 1px solid #000; padding: 0.15em 0.25em; text-align: center; }
td:nth-child(2), th:nth-child(2) { text-align: left; }
tr.star td { font-weight: bold; }
.scoreboard, .stats, .results, .quotes, .verdicts, .tips, .leaders { margin: 1em 0; }
.scoreboard { border: 3px solid #000; padding: 0.5em; text-align: center; }
.scoreboard div { margin: 0.1em 0; }
.scoreboard__score { font-size: 2.2em; font-weight: bold; }
.scoreboard__meta { font-size: 0.8em; text-transform: uppercase; }
.stat, .rcard, .quote, .verdict, .tip, .leader { border-top: 1px solid #000; padding: 0.4em 0; }
.stat b { font-size: 1.4em; display: block; }
.rcard__line { font-weight: bold; }
.rcard__scorers, .rcard__tag, .meter, .lvl, .role, .leader__league, .leader__pts { font-size: 0.85em; }
.quote blockquote { margin: 0.2em 0; font-style: italic; }
.who { font-weight: bold; text-transform: uppercase; font-size: 0.85em; }
.verdict h5, .tip h5 { font-size: 1.05em; text-transform: uppercase; }
.key { font-size: 0.8em; }
.key i { display: none; }
.cover-img { text-align: center; margin: 0; padding: 0; }
.cover-img img { max-width: 100%; }
.toc li { margin-bottom: 0.4em; }
.checklist { list-style: square; }
"""


def xhtml_doc(title: str, body: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en-AU" xml:lang="en-AU">
<head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
{body}
</body>
</html>"""


def epubify(fragment: str, images: dict[str, str]) -> str:
    """Turn a web fragment into Kindle-friendly XHTML."""
    s = fragment
    s = re.sub(r'<div class="web-only">.*?</div><!--/web-only-->', "", s, flags=re.S)
    s = s.replace('<div class="epub-only">', "<div>").replace("<!--/epub-only-->", "")
    # swap every rendered graphic for its greyscale PNG
    def swap(m: re.Match) -> str:
        gid = m.group(1)
        if gid not in images:
            raise SystemExit(f"epub: no rendered image for graphic '{gid}'. Run build/render.mjs first.")
        return f'<img src="images/{images[gid]}" alt=""/>'
    s = re.sub(r'<div class="g[^"]*" data-epub="([\w-]+)"[^>]*>.*?</div><!--/g-->', swap, s, flags=re.S)
    s = re.sub(r'<img src="img/([\w-]+)\.(?:jpg|png)"', r'<img src="images/photo-\1.jpg"', s)
    s = re.sub(r'(<img [^>]*?)\s*/?>', lambda m: m.group(1).rstrip("/ ") + "/>", s)
    if "<svg" in s:
        raise SystemExit("epub: an inline <svg> survived outside a .g[data-epub] block.")
    # web-only niceties that mean nothing on paper
    s = re.sub(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", r'<p class="small"><i>\1:</i> \2</p>', s, flags=re.S)
    s = re.sub(r'\s(title|loading|aria-[\w-]+)="[^"]*"', "", s)
    return s


def to_greyscale(src: Path, dst: Path, max_w: int = 1200) -> None:
    from PIL import Image, ImageOps
    im = Image.open(src).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    g = ImageOps.grayscale(im)
    g = ImageOps.autocontrast(g, cutoff=0.5)
    g.save(dst, optimize=True)


def build_epub() -> None:
    for key, mag in MAGS.items():
        if mag["src"].exists():
            for issue in load_issues(key):
                build_issue_epub(issue)


def build_issue_epub(issue: dict) -> None:
    from PIL import Image, ImageOps
    if True:
        mag = issue["mag"]
        slug = issue["slug"]
        rendered = RENDER_OUT / mag["key"] / slug
        if not (rendered / "cover.png").exists():
            raise SystemExit(f"epub: {rendered}/cover.png missing — run `node build/render.mjs` first.")
        work = RENDER_OUT / slug / "epub"
        if work.exists():
            shutil.rmtree(work)
        (work / "images").mkdir(parents=True)

        # images
        images: dict[str, str] = {}
        for png in sorted(rendered.glob("g-*.png")):
            name = png.stem + ".png"
            to_greyscale(png, work / "images" / name)
            images[png.stem] = name
        photos = []
        img_files = sorted(issue["dir"].glob("img/*.jpg")) + sorted(issue["dir"].glob("img/*.png"))
        for jpg in img_files:
            src = ImageOps.exif_transpose(Image.open(jpg))
            if src.mode in ("RGBA", "LA", "P"):          # transparent game renders: put them on white
                src = src.convert("RGBA")
                bg = Image.new("RGBA", src.size, (255, 255, 255, 255))
                bg.alpha_composite(src)
                src = bg
            g = ImageOps.grayscale(src.convert("RGB"))
            g.thumbnail((1000, 1000))
            g = ImageOps.autocontrast(g, cutoff=0.3)
            name = f"photo-{jpg.stem}.jpg"
            g.save(work / "images" / name, quality=80, optimize=True)
            photos.append(name)
        cover = Image.open(rendered / "cover.png").convert("L")
        cover.thumbnail((1200, 1600))
        cover.save(work / "images" / "cover.jpg", quality=88)

        glossary_html = build_glossary(issue)
        chapters = []
        for i, a in enumerate(issue["articles"]):
            frag = glossary_html if a["file"] == "@glossary" else read_fragment(issue, a["file"])
            frag = re.sub(r'(href=")([\w-]+)\.html"', r'\1ch\2.xhtml"', frag)
            body = (f'<section epub:type="chapter">\n<p class="kicker">{a["section"]} · p.{a["page"]}</p>\n'
                    f'<h1>{strip_tags(a["title_html"])}</h1>\n<p class="dek">{a["dek"]}</p>\n'
                    f'<p class="byline">{a["byline"]}</p>\n{epubify(frag, images)}\n</section>')
            name = f"ch{a['slug']}.xhtml"
            doc = xhtml_doc(strip_tags(a["title_html"]), body)
            try:
                ET.fromstring(doc.split("\n", 2)[2])   # well-formedness check (skip decl + doctype)
            except ET.ParseError as e:
                (work / name).write_text(doc, encoding="utf-8")
                raise SystemExit(f"epub: {name} is not well-formed XHTML: {e}\n  (written to {work / name})")
            (work / name).write_text(doc, encoding="utf-8")
            chapters.append((name, strip_tags(a["title_html"]), a))

        cover_x = xhtml_doc("Cover", f'<div class="cover-img"><img src="images/cover.jpg" alt="{html.escape(mag["title"])} cover"/></div>')
        (work / "cover.xhtml").write_text(cover_x, encoding="utf-8")

        letter = ""
        if issue.get("editor_letter"):
            lf = read_fragment(issue, issue["editor_letter"])
            lf = re.sub(r"<section[^>]*>|</section>|<div[^>]*>|</div>", "", lf)
            letter = lf
        toc_items = "".join(f'<li><a href="{n}">{html.escape(t)}</a> — <i>{a["section"]}</i></li>' for n, t, a in chapters)
        disclaimer = f'<p class="small"><i>{mag["disclaimer"]}</i></p>' if mag["disclaimer"] else ""
        contents = xhtml_doc("Contents", f'<h1>Inside Issue {issue["number"]}</h1>\n<p class="byline">{html.escape(issue["date_display"])}</p>\n'
                                         f'<ol class="toc">{toc_items}</ol>\n{letter}\n{disclaimer}')
        (work / "contents.xhtml").write_text(contents, encoding="utf-8")

        nav = xhtml_doc("Contents", '<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>'
                        + '<li><a href="contents.xhtml">Inside this issue</a></li>'
                        + "".join(f'<li><a href="{n}">{html.escape(t)}</a></li>' for n, t, _ in chapters)
                        + "</ol></nav>")
        (work / "nav.xhtml").write_text(nav, encoding="utf-8")
        (work / "style.css").write_text(EPUB_CSS, encoding="utf-8")

        book_id = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, SITE_URL + mag['path'] + 'issue/' + slug)}"
        title = f"{mag['title']} — Issue {issue['number']} ({issue['date_display']})"
        modified = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                    '<item id="css" href="style.css" media-type="text/css"/>',
                    '<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
                    '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
                    '<item id="contents" href="contents.xhtml" media-type="application/xhtml+xml"/>',
                    '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>']
        manifest += [f'<item id="img-{Path(f).stem}" href="images/{f}" media-type="image/png"/>' for f in images.values()]
        manifest += [f'<item id="{Path(f).stem}" href="images/{f}" media-type="image/jpeg"/>' for f in photos]
        manifest += [f'<item id="c{i}" href="{n}" media-type="application/xhtml+xml"/>' for i, (n, _, _) in enumerate(chapters)]
        spine = ['<itemref idref="cover"/>', '<itemref idref="contents"/>'] + [f'<itemref idref="c{i}"/>' for i in range(len(chapters))]
        opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en-AU">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{book_id}</dc:identifier>
    <dc:title>{html.escape(title)}</dc:title>
    <dc:creator>{html.escape(mag['title'])}</dc:creator>
    <dc:publisher>{html.escape(mag['title'])}</dc:publisher>
    <dc:language>en-AU</dc:language>
    <dc:date>{issue['date']}</dc:date>
    <dc:description>{html.escape(issue['description'])}</dc:description>
    <meta property="dcterms:modified">{modified}</meta>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
    {chr(10).join('    ' + m for m in manifest).strip()}
  </manifest>
  <spine toc="ncx">
    {' '.join(spine)}
  </spine>
  <guide><reference type="cover" title="Cover" href="cover.xhtml"/><reference type="toc" title="Contents" href="contents.xhtml"/></guide>
</package>"""
        ncx_points = "".join(
            f'<navPoint id="np{i}" playOrder="{i+1}"><navLabel><text>{html.escape(t)}</text></navLabel><content src="{n}"/></navPoint>'
            for i, (n, t, _) in enumerate([("contents.xhtml", "Inside this issue", None)] + chapters))
        ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head><meta name="dtb:uid" content="{book_id}"/></head>
<docTitle><text>{html.escape(title)}</text></docTitle>
<navMap>{ncx_points}</navMap>
</ncx>"""
        (work / "content.opf").write_text(opf, encoding="utf-8")
        (work / "toc.ncx").write_text(ncx, encoding="utf-8")

        home = DOCS / mag["path"] if mag["path"] else DOCS
        out = home / "issues" / slug / f"{mag['epub']}-{slug}.epub"
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w") as z:
            z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            z.writestr("META-INF/container.xml", """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>""", compress_type=zipfile.ZIP_DEFLATED)
            for f in sorted(work.rglob("*")):
                if f.is_file():
                    z.write(f, "OEBPS/" + f.relative_to(work).as_posix(), compress_type=zipfile.ZIP_DEFLATED)
        # colour cover for the website / archive
        shutil.copy(rendered / "cover.png", home / "issues" / slug / "cover.png")
        print(f"epub: {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB, {len(images)} graphics)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "web"
    {"web": build_web, "epub": build_epub}[cmd]()
