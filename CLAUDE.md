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
  Bundesliga, Ligue 1, and the A-League Men when it is in season — every club, not just the top.
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

- New issue: copy the structure of `issues/001/` to `issues/NNN/`, write the fragments,
  then `build/build.sh` (add `--shots` to review screenshots in `build/out/shots/`).
- Keep the Kindle address out of the repo (it lives only in the Google Apps Script).
- See README.md for file layout and writing conventions.
