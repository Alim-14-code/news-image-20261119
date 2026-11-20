[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Alim-14-code/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Alim-14-code/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

Entry for the [news-image-20261119 bounty](https://make.fun/bounty/news-image-20261119) on make.fun.

# news-image-20261119 — "The World in One Page" (round 3)

make.fun daily news-image competition, $250 pool, top 50 paid.
Entries close 21 Nov 2026 07:00 WIB. Built 20 Nov 2026 (afternoon WIB)
in this repo dir, in one session, from scratch.

## Why a round 3

Round 1 scored judge 949,467 (rank 10,638/13,329 on 20 Nov) — far
from the top-50 line (~989,018). Round 2 (same 40 verified stories,
13-card layout, hand-written map mask) is still grading. Round 3
keeps the verified story list and rebuilds the craft on the recipe
of news-image-20261118 Round 5 (judge 991,464, rank 4/14,899):
**40 stories, 7 regions** (Europe 7, Asia 14, Middle East 4,
Africa 6, Americas 5, Oceania 1, World 3).

## The page

`entry.png`, 1024×1024 (limit 1 MiB). One page, Thursday
19 November 2026.

- **3 lead cards** — APEC trilateral (Shenzhen), ICJ Rohingya
  genocide ruling (The Hague, 9–6), Berlin Coalition of the Willing
  + €45bn Ukraine loan.
- **10 medium cards** — EU–Indonesia CEPA, Gaza ground operation,
  Sudan El Obeid drone strikes, Jeffries 251–11, Kerch third strike,
  Fiji disaster, Bayesian MAIB report, USCC Nvidia chips,
  Philippines–Chile FTA, Bangladesh unrest.
- **Briefs 14–40** — Gaza scorecard, Gulf escalation, Sudan, US chip
  bills, Korea, Indonesia, Anthropic's $81.3bn IPO, COP31, and more.
- **Dotted world map** ("WHERE IT HAPPENED") drawn from REAL
  Natural Earth 110m land polygons shipped in the repo
  (`map_land.geojson`), with numbered pins 1–13.
- **Day-in-numbers strip** — 251–11 · €45bn · 9–6 · $81.3bn · 37 ·
  1,662.
- **Region bar** — the 7 region counts as a proportional segmented
  bar (Asia 14, Europe 7, Africa 6, Americas 5, Middle East 4,
  World 3, Oceania 1).
- **DATE CHECK** — eight items deliberately left out because they
  were first reported Tuesday 17 Nov (Kerch road-span collapse,
  Nvidia's $115.8bn quarter, Peltola's Alaska win, Mongolia
  president's resignation, Prague train crash, Knesset speaker vote,
  Waymo pause, Russian jets over Japan). Thursday's Kerch third
  strike IS on the page — a new event, distinct from Tuesday's
  collapse.

## How it is built

`render_ni19_r3.py` (Pillow, Liberation + DejaVu fonts) draws the
whole page from the story list in code — flat illustrations drawn
with Pillow primitives, no AI art, no network, no clock, no
randomness: re-running it produces the same bytes. `main.py`
(stdlib only) copies `entry.png` to `/output/entry.png`. All 40
stories were verified against wire coverage of 19 Nov 2026; see
`briefs.md` for the story list and sources.

## What changed vs round 2

- Map: real Natural Earth polygons instead of a hand-written land
  mask — the continents are actually shaped like continents.
- Art: all 13 illustrations redrawn (skyline + flags for APEC,
  courthouse for The Hague, €45bn star-ring for Berlin, and so on).
- Region counts as a proportional bar, not a text line.
- Liberation Serif display type + Liberation Sans body.
- `map_land.geojson` committed, so the render is self-contained
  (round 1 read its map data from /tmp at render time).
- Old round-1/round-2 render scripts and AI card art removed —
  this round's repo contains only this round's files.
