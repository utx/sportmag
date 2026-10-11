#!/usr/bin/env python3
"""Fetch full, current league tables from BBC Sport and write them as Touchline table HTML.

    python3 build/league_tables.py issues/002/tables-full.html

Paste or include the output in the issue's tables article. Every league in LEAGUES is
printed in full (all clubs), with Champions League places and the relegation zone marked.
"""
import html
import re
import sys
import urllib.request

# (BBC slug, caption, country, top places shaded, relegation places shaded)
LEAGUES = [
    ("premier-league", "Premier League", "England", 4, 3),
    ("spanish-la-liga", "La Liga", "Spain", 4, 3),
    ("italian-serie-a", "Serie A", "Italy", 4, 3),
    ("german-bundesliga", "Bundesliga", "Germany", 4, 2),
    ("french-ligue-one", "Ligue 1", "France", 3, 2),
    ("australian-a-league", "A-League Men", "Australia", 6, 0),   # top six = finals places
]
SHORT = {
    "Manchester City": "Man City", "Manchester United": "Man Utd", "Brighton & Hove Albion": "Brighton",
    "Tottenham Hotspur": "Spurs", "Nottingham Forest": "Nott'm Forest", "Newcastle United": "Newcastle",
    "Leeds United": "Leeds", "Ipswich Town": "Ipswich", "Hull City": "Hull", "Coventry City": "Coventry",
    "Bayer 04 Leverkusen": "Bayer Leverkusen", "Borussia M'gladbach": "Gladbach", "Olympique Lyonnais": "Lyon",
    "Racing de Santander": "Racing Santander", "Sydney": "Sydney FC", "Auckland": "Auckland FC", "Deportivo de A Coruña": "Deportivo La Coruña",
}
STAR = {"Manchester United", "Sydney FC", "Sydney"}   # our teams get the highlighted row


def fetch(slug: str) -> list[list]:
    url = f"https://www.bbc.com/sport/football/{slug}/table"
    page = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode()
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [" ".join(html.unescape(re.sub(r"<[^>]+>", " ", c)).split()) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        if cells and cells[0] != "Team" and re.match(r"\d+ ", cells[0]):
            pos, team = cells[0].split(" ", 1)
            rows.append([int(pos), team] + [int(x) for x in cells[1:9]])
    if not rows:
        raise SystemExit(f"no table rows found for {slug}; has the BBC page layout changed?")
    return rows


def render(rows, caption, country, top, bottom) -> str:
    n = len(rows)
    out = [f'<div class="ltable-wrap wide">\n<table class="ltable">\n  <caption>{caption}<small>{country} · BBC Sport table</small></caption>',
           "  <thead><tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead>\n  <tbody>"]
    for pos, team, p, w, d, l, _gf, _ga, gd, pts in rows:
        cls = []
        if pos <= top:
            cls.append("ucl")
        if bottom and pos > n - bottom:
            cls.append("rel")
        if pos == top or (bottom and pos == n - bottom):
            cls.append("split")
        if team in STAR:
            cls.append("star")
        gds = f"+{gd}" if gd > 0 else ("0" if gd == 0 else f"−{abs(gd)}")
        attr = f' class="{" ".join(cls)}"' if cls else ""
        out.append(f'    <tr{attr}><td>{pos}</td><td>{html.escape(SHORT.get(team, team))}</td><td>{p}</td><td>{w}</td>'
                   f'<td>{d}</td><td>{l}</td><td>{gds}</td><td class="pts">{pts}</td></tr>')
    out.append("  </tbody>\n</table>\n</div>")
    key = ("Finals places" if caption.startswith("A-League") else "Champions League places")
    out.append(f'<div class="key"><span><i style="background:#63a9df"></i>{key}</span>'
               + ('<span><i style="background:#d01f27"></i>Relegation zone</span>' if bottom else "") + "</div>")
    return "\n".join(out)


if __name__ == "__main__":
    parts = []
    for slug, caption, country, top, bottom in LEAGUES:
        rows = fetch(slug)
        parts.append(render(rows, caption, country, top, bottom))
        print(f"{caption}: {len(rows)} clubs", file=sys.stderr)
    text = "\n\n".join(parts) + "\n"
    if len(sys.argv) > 1:
        open(sys.argv[1], "w", encoding="utf-8").write(text)
    else:
        sys.stdout.write(text)
