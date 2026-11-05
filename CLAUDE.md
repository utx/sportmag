# Touchline — editorial brief for every issue

Touchline is a weekly football, sport and games magazine for a bright 9-year-old in Sydney,
published at https://utx.github.io/sportmag/ with a one-tap Send to Kindle button.
It should read like a proper product: no reader names or personal references anywhere.

## Standing requirements (from the publisher)

- **Always based on recent events.** Check every score, quote and stat against full reports
  (BBC Sport, club sites, ABC, etc.) before writing. Never invent quotes; attribute real ones.
- **Manchester United is the main focus**: full match report of their latest game and a preview
  of the next one. Subtly biased in United's favour and against big rivals (Liverpool, Man City),
  but the facts underneath must stay accurate.
- **Sydney FC is the local focus**, with an emphasis on actually going to live games
  (tickets, getting there, where to sit, what to bring, upcoming home dates).
- Shorter reviews of other Premier League games and the big La Liga clubs (Barcelona, Real Madrid,
  plus Atlético when relevant).
- **Full league tables from the major leagues in every issue**: Premier League, La Liga, Serie A,
  Bundesliga, Ligue 1, the Scottish Premiership, and the A-League Men when it is in season — every club, not just the top.
  Generate them with `python3 build/league_tables.py <out.html>` (BBC Sport data) and include
  them in the tables article; add the "who's on top" summary cards above them.
- Shorter sections on other sports: rugby (union and league), NBA, tennis.
- Games section, Fortnite first, plus other age-appropriate games (no M/R-rated titles).
- Push vocabulary: Word Watch boxes in every article (they feed the Word Bank automatically),
  a quiz at the back.
- Plenty of visuals: hand-built SVG graphics (not AI-looking) plus freely licensed photos from
  Wikimedia Commons with photographer/licence credits in `issues/NNN/photos.json`. Never use
  agency/news-site photos.

## Mechanics

- **Before building any issue, read `inbox/README.md`** for publisher requests (images, article ideas)
  and include them; then mark them done there.
- New issue: copy the structure of `issues/001/` to `issues/NNN/`, write the fragments,
  then `build/build.sh` (add `--shots` to review screenshots in `build/out/shots/`).
- Keep the Kindle address out of the repo (it lives only in the Google Apps Script).
- See README.md for file layout and writing conventions.

---

# The Chug Jug — brief for the sister magazine

An unofficial Fortnite fan magazine for the same reader, published at
https://utx.github.io/sportmag/chugjug/ (issues in `chugjug/issues/NNN/`, same build).

- Name stays "The Chug Jug", with "An unofficial Fortnite fan magazine" under the masthead.
  Puns on Chug Jugs and other in-game items throughout (section names, headings, ratings
  out of five Chug Jugs).
- Epic's Fan Content Policy (https://legal.epicgames.com/epicgames/fan-art-policy) applies:
  the disclaimer is in every page footer and the Kindle edition (MAGS config in build.py);
  never look official, never link to cheats/hacks, non-commercial only.
- Images: Epic's own assets only. Use fortnite-api.com (v1/map with POI coordinates,
  v2/shop, v2/cosmetics, v2/news/br) and Epic's lobby news art. Do NOT show official art of
  collaboration characters owned by other companies (Sonic, Pac-Man, FNAF, Marvel, horror
  films, celebrities, etc.) — filter by `series`/`set`; mention them in text only. Credit
  images in photos.json with {"credit": "Image: Epic Games / Fortnite"}.
- Map markers: world (x, y) -> 2048px map image: px = 975 + 0.00658·x, py = 1016 + 0.00661·y
  (re-check against the labelled map each season).
- Age-appropriate: skip horror collabs in picks, never pressure spending, "ask a grown-up".
- Fortnite.com blocks automated access; use fortnite-api.com plus several news write-ups
  (cross-check) for patch details.
- Kindle: issue codes are prefixed "cj" (e.g. cj001); kindle/Code.gs handles both magazines.

---

# LEGO® Star Wars™ fan book — image permissions and brief

A fan book (in `books/<slug>/`, built with `build/book.py`) reviewing the latest LEGO Star Wars
sets, with pros and cons for each, for the same reader. Go heavy on photos.

## Image permissions (from the publisher, 5 Nov 2026)

These replace the Wikimedia-Commons-only rule **for LEGO content** (this book and any LEGO
content in the magazines):

- **Official LEGO product photos: always OK, as many as you like.** The publisher has the
  LEGO Group's permission to use them without limit. Credit each one in photos.json as
  `{"credit": "Image: The LEGO Group, used with permission"}`.
- **Fan-site photos: OK from these named sites only**, where the publisher has permission:
  Brickset, Brick Fanatics, Rebrickable (minifigure images; the publisher supplied an API key,
  which lives outside the repo and must never be committed). Credit the site and, where shown,
  the photographer, e.g. `{"credit": "Photo: Brick Fanatics, used with permission"}`.
  To add another site, the publisher names it here first. Photos from sites that are not
  listed, and other random photos found on the web, are not covered.
- Keep the source URL of every downloaded image in photos.json so credits can be checked.

## Mechanics

- The first book is `books/stud-wars/` ("Stud Wars"). It is **Kindle only**: `"kindle_only": true` in
  book.json keeps the EPUB in `build/out/book/stud-wars/` (never docs/), and its photos stay out of
  the public repo (`books/stud-wars/img/` is git-ignored). `build/book.sh stud-wars --kindle`
  re-downloads them from the source URLs in photos.json (`build/book_fetch.py`), then builds.
- Set facts live in `books/stud-wars/sets.json` (from Brickset); each review is a
  `<set id="75460-1" rating=".." play=".." display=".." value="..">` block, and the builder adds the
  photo, rating card, facts table, extra photos and minifigure strip from photos.json.
- LEGO.com blocks automated access; use Brickset's public pages (set lists, set pages, reviews,
  news) and images.brickset.com. Don't try to get round blocked endpoints.
- The publisher also has a **Brickset API key** (kept outside the repo, never committed). Its
  `getAdditionalImages` call gives LEGO's own extra product photos per set (box, lifestyle,
  feature shots), and `getSets` gives prices for the US, UK, Canada and Germany, but not Australia.
- Story backgrounds ("From the screen" boxes) live in `books/stud-wars/lore.json`; highlighted story
  words go in each chapter's "Word Watch: story words" box.

## Brief

- Writing pros and cons: we haven't built the sets ourselves, so attribute opinions to named
  reviewers ("Brickset's reviewer found…") and keep the facts (pieces, minifigures, price,
  age) checked against LEGO's own listings. Prices are LEGO's US prices in US$ (no source for
  Australian prices can be reached automatically), with the date we checked; explain the exchange rate.
- Ratings are out of five 2×4 bricks. Word Watch boxes throughout, quiz at the back.
- Footer and Kindle edition say it's an unofficial fan book, not made by the LEGO Group or
  Lucasfilm.
- Never pressure spending: present the big sets as a wish list, and add "ask a grown-up".
