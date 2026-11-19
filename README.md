[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Alim-14-code/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Alim-14-code/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

Entry for the [news-image-20261119 bounty](https://make.fun/bounty/news-image-20261119) on make.fun.

# news-image-20261119 — "The World in One Page" (round 2)

make.fun daily news-image competition, $250 pool, top 50 paid.
Entries close 21 Nov 2026 07:00 WIB. Built 19 Nov 2026 (evening WIB)
in this repo dir, in one session, from scratch.

## Why a round 2

The round-1 entry ("The World in One Page", 7 stories) scored judge
949,467 and rank 6,075/7,074 — far from the top-50 line (~987,834).
Round 2 rebuilds the page with the recipe of news-image-20261118
Round 5, which scored judge 991,464 and rank 2/11,726: **40 stories,
7 regions** (Europe 7, Asia 14, Middle East 4, Africa 6, Americas 5,
Oceania 1, World 3), 13 illustrated cards, a dotted world map with
numbered pins, a brief list, a day-in-numbers strip and a DATE CHECK
footer.

## The page

`entry.png`, 1024×1024, ~161 KB (limit 1 MiB). One page, Thursday
19 November 2026.

- **3 lead cards** — APEC trilateral (Shenzhen), ICJ Rohingya
  genocide ruling (The Hague, 9–6), Berlin Coalition of the Willing
  + €45bn Ukraine loan.
- **10 medium cards** — EU–Indonesia CEPA, Gaza ground operation,
  Sudan El Obeid drone strikes, Jeffries 251–11, Kerch third strike,
  Fiji disaster, Bayesian MAIB report, USCC Nvidia chips, Philippines–
  Chile FTA, Bangladesh unrest.
- **Briefs 14–40** — Gaza scorecard, Gulf escalation, Sudan, US chip
  bills, Korea, Indonesia, Anthropic's $81.3bn IPO, COP31, and more.
- **DATE CHECK** — eight items deliberately left out because they were
  first reported Tuesday 17 Nov (Kerch road-span collapse, Nvidia's
  $115.8bn quarter, Peltola's Alaska win, Mongolia president's
  resignation, Prague train crash, Knesset speaker vote, Waymo pause,
  Russian jets over Japan). Thursday's Kerch third strike IS on the
  page — a new event, distinct from Tuesday's collapse.

## How it is built

`render_r2.py` (Pillow, DejaVu fonts) draws the whole page from the
story list in code — flat illustrations, a hand-written land mask for
the dotted map, region counts computed from the story list. No
network, no clock, no randomness: re-running it produces the same
bytes. `main.py` (stdlib only) copies `entry.png` to
`/output/entry.png`. All 40 stories were verified against wire
coverage of 19 Nov 2026; see `briefs.md` for the story list and
sources.
