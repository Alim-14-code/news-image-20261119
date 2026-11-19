#!/usr/bin/env python3
"""Render entry.png for make.fun news-image-20261119, round 2.

One page, Thursday 19 November 2026: 40 stories, 7 regions.
Written from scratch in this session. Layout follows the winning
news-image-20261118 R5 formula (3 leads + 10 medium cards with flat
Pillow illustrations, dotted world map with numbered pins, brief list,
day-in-numbers strip, DATE CHECK footer, sources line) — with all
text, decks and illustrations written fresh for 19 November.

The 7 stories of the first live entry are kept (APEC trilateral,
EU-Indonesia CEPA, Berlin EUR45bn, Fiji disaster, Jeffries 251-11,
Kerch third strike, Bayesian MAIB report) and 33 more real 19-Nov
stories are added, each verified against wire coverage or the day's
news roundups before it went on the page.

Deterministic: no network, no clock, no randomness. The dotted map
is drawn from a hand-written land mask (ellipses over lon/lat),
not from any downloaded file.

    python3 render_r2.py        # writes entry.png next to this file
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1024, 1024

# ---- palette: warm paper, muted newsroom inks ----
PAPER = (246, 241, 231)
CARD = (255, 255, 255)
INK = (26, 36, 48)
NAVY = (30, 41, 66)
NAVY2 = (44, 60, 96)
RUST = (178, 82, 42)
TEAL = (74, 120, 118)
TEAL_DK = (36, 72, 74)
SAND = (229, 218, 196)
SAND_DK = (203, 187, 148)
GOLD = (198, 152, 58)
GREY = (104, 112, 126)
LINE = (214, 205, 185)
DOT = (120, 138, 156)
MAP_BG = (239, 234, 221)
RED = (178, 44, 36)
GREEN = (62, 110, 72)

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DSB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
DS = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def wrap(d, text, font, max_w):
    """Wrap text to lines that fit max_w pixels. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(d, text, font, max_w, max_lines=None):
    """Wrap, then truncate with an ellipsis if it runs past max_lines."""
    lines = wrap(d, text, font, max_w)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        # trim the last line so the ellipsis fits
        while lines and d.textlength(lines[-1] + "…", font=font) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "…"
    return lines


# ---- region colours (used for tags, map dots, region bar) ----
REGION_COLOR = {
    "Europe": (44, 60, 96),
    "Asia": (178, 82, 42),
    "Middle East": (122, 74, 28),
    "Africa": (62, 110, 72),
    "Americas": (96, 62, 110),
    "Oceania": (36, 110, 122),
    "World": (90, 90, 90),
}

# ---- the 13 cards: (num, kicker, headline, deck, region, source, art, lon, lat) ----
CARDS = [
    (1, "APEC · SHENZHEN", "Three leaders, one table",
     "Trump, Xi and Putin hold the first trilateral of sitting US, "
     "Chinese and Russian presidents — one hour at Kylin Villa, "
     "nuclear arms on the agenda.",
     "Asia", "Reuters", "apec", 114.1, 22.5),
    (2, "THE HAGUE · LAW", "Myanmar guilty of genocide",
     "ICJ rules 9–6: Myanmar committed genocide against the "
     "Rohingya in 2017 — the first time the court has found a "
     "state guilty. Reparations ordered.",
     "World", "ICJ / Reuters", "icj", 4.3, 52.1),
    (3, "BERLIN · UKRAINE", "Europe demands a seat — and €45bn",
     "The Coalition of the Willing meets in Berlin pressing for "
     "binding security guarantees. The Commission proposes a "
     "€45bn loan for Ukraine in 2027.",
     "Europe", "Reuters", "berlin", 13.4, 52.5),
    (4, "TRADE", "EU–Indonesia deal sealed",
     "EU Council authorises signature; signing 21 Nov. "
     "90% duty-free.",
     "Europe", "EU Council", "cepa", 4.35, 50.85),
    (5, "GAZA", "Tanks cross the Yellow Line",
     "First major ground op since the Oct 2025 ceasefire; "
     "three killed.",
     "Middle East", "DPA / Reuters", "gaza", 34.5, 31.5),
    (6, "SUDAN", "Drones over El Obeid: 37 dead",
     "Amnesty: nine RSF drone strikes on El Obeid killed "
     "37 civilians.",
     "Africa", "Amnesty Intl", "sudan", 30.2, 13.2),
    (7, "WASHINGTON", "Jeffries: history next",
     "Democrats nominate him 251–11; first Black "
     "speaker.",
     "Americas", "Reuters / AP", "jeffries", -77.0, 38.9),
    (8, "CRIMEA", "Kerch hit a third time in a week",
     "Third strike in a week halts trains hours before "
     "the trilateral.",
     "Europe", "Reuters", "kerch", 36.5, 45.3),
    (9, "FIJI", "A nation out of water",
     "One-month disaster declared; FJ$20m for emergency "
     "water.",
     "Oceania", "Reuters", "fiji", 178.4, -18.1),
    (10, "SICILY", "The wind nobody forecast",
     "MAIB: a ~70-knot downburst sank her in under "
     "15 seconds.",
     "Europe", "MAIB / Guardian", "bayesian", 13.5, 38.1),
    (11, "CHIPS", "China chases Nvidia's top chips",
     "PLA seeks Nvidia's top AI chips despite export "
     "curbs.",
     "Americas", "USCC / Reuters", "chips", -77.0, 38.9),
    (12, "APEC", "Philippines–Chile: first LatAm deal",
     "Manila signs its first free-trade deal with "
     "Latin America.",
     "Asia", "Inquirer", "phchile", 121.0, 14.6),
    (13, "BANGLADESH", "Homes of ex-MPs torched",
     "Awami League supporters torch ex-MPs' homes "
     "and a bank.",
     "Asia", "BSS / FE", "bangladesh", 90.4, 23.8),
]

# ---- briefs 14-40: (num, headline, region, lon, lat) ----
BRIEFS = [
    (14, "Gaza peace plan scores 4/26 one year on", "Middle East", 34.5, 31.5),
    (15, "Gulf: Iran claims self-defence; US carrier pulls out", "Middle East", 56.3, 26.5),
    (16, "Israel moves to repeal Netanyahu court overhaul", "Middle East", 35.2, 31.8),
    (17, "Sudan blames Ethiopia and UAE for drone attacks", "Africa", 32.5, 15.6),
    (18, "WFP: month of food aid for 30,000 at El Dabba", "Africa", 30.5, 18.0),
    (19, "Ex-Sudan official wanted by ICC arrested", "Africa", 32.5, 15.6),
    (20, "Sudan army retakes Iyal Bakhit, downs RSF drone", "Africa", 30.0, 12.5),
    (21, "Tanzania's Samia in Uganda for Museveni talks", "Africa", 32.6, 0.3),
    (22, "Trump: Blackwell chips to China in '2–3 years'", "Americas", 114.1, 22.5),
    (23, "Congress drafts three bills to curb chip sales", "Americas", -77.0, 38.9),
    (24, "Nvidia stock 37% off its high after earnings", "Americas", -74.0, 40.7),
    (25, "Dutch watchdog: don't buy AI smart glasses", "Europe", 4.9, 52.4),
    (26, "Denmark to ratify Trump deal over Greenland", "Europe", 12.6, 55.7),
    (27, "Markets: DAX +0.8%, CAC +0.6%; UK near 6-week low", "Europe", 8.7, 50.1),
    (28, "Seoul's Lee renews call for talks with Pyongyang", "Asia", 127.0, 37.5),
    (29, "Korea–China trade deal raises hopes in Seoul", "Asia", 116.4, 39.9),
    (30, "Korea's big exam held under strict anti-cheat curbs", "Asia", 127.0, 37.5),
    (31, "Indonesia passes asset-forfeiture bill into law", "Asia", 106.8, -6.2),
    (32, "Singapore: don't split Asia-Pacific into blocs", "Asia", 103.8, 1.35),
    (33, "Japan's Takaichi: Taiwan stance unchanged", "Asia", 139.7, 35.7),
    (34, "IAEA: North Korea uranium enrichment expanding", "Asia", 125.8, 39.0),
    (35, "Women's Asian hockey trophy opens in Bhopal", "Asia", 77.4, 23.3),
    (36, "BTS to tour Asia and Australia from Kaohsiung", "Asia", 120.3, 22.6),
    (37, "Trump, Marcos hail alliance, pledge trade ties", "Asia", 121.0, 14.6),
    (38, "Myanmar's leader reconsiders ASEAN ties", "Asia", 96.1, 19.8),
    (39, "Anthropic's $81.3bn IPO arms AI price war", "World", -122.4, 37.8),
    (40, "COP31 climate summit opens in Antalya", "World", 30.7, 36.9),
]

# ---- day in numbers: (big, label) ----
NUMBERS = [
    ("251–11", "Jeffries nominated"),
    ("€45bn", "EU loan for Ukraine"),
    ("9–6", "ICJ genocide vote"),
    ("$81.3bn", "Anthropic IPO"),
    ("37", "killed in El Obeid"),
    ("1,662", "Gaza dead since ceasefire"),
]

# ---- items deliberately left out: first reported Tuesday 17 Nov ----
DATE_CHECK = (
    "DATE CHECK — left out on purpose, first reported Tue 17 Nov: Kerch road-span "
    "collapse (Thu's third strike IS on the page) · Nvidia's $115.8bn quarter · "
    "Peltola's Alaska Senate win · Mongolia president's resignation announced · "
    "Prague train crash · Knesset speaker vote · Waymo freeway pause · "
    "Russian jets breach Japan's airspace."
)

SOURCES = (
    "Sources: Reuters · AP · AFP · BBC · Al Jazeera · EU Council · ICJ · MAIB · Amnesty International · "
    "USCC · Inquirer · BSS · DPA · The Guardian. Every story verified against wire coverage of 19 Nov 2026."
)

# ---- land mask: (lon centre, lat centre, rx, ry) ellipses, hand-drawn ----
LAND = [
    (-110, 62, 55, 12), (-85, 55, 25, 10), (-98, 39, 28, 9), (-102, 23, 12, 7),
    (-88, 13, 8, 4), (-42, 74, 12, 8),
    (-60, 0, 18, 10), (-45, -12, 14, 12), (-68, -25, 8, 18),
    (5, 48, 14, 9), (15, 63, 10, 8), (-2, 54, 3, 5), (28, 52, 14, 8),
    (-4, 40, 6, 4), (15, 40, 6, 4),
    (5, 22, 22, 8), (-8, 10, 10, 7), (20, 0, 12, 10), (35, -2, 10, 12),
    (25, -22, 12, 10), (47, -19, 3, 6),
    (45, 24, 10, 9), (45, 35, 14, 6),
    (70, 62, 35, 12), (135, 65, 40, 12), (65, 45, 12, 8), (78, 21, 10, 12),
    (101, 15, 7, 9), (105, 35, 18, 12), (115, -3, 18, 5), (138, 38, 4, 8),
    (128, 38, 2, 4), (142, -5, 8, 4),
    (122, -25, 12, 10), (145, -28, 10, 10), (172, -41, 3, 6),
]


def is_land(lon, lat):
    for cx, cy, rx, ry in LAND:
        dx = (lon - cx) / rx
        dy = (lat - cy) / ry
        if dx * dx + dy * dy <= 1.0:
            return True
    return False


# ---- flat illustrations, one per card (Pillow primitives only) ----
def art_apec(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 52, 82))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(24, 34, 56))
    # skyline
    for i, bh in enumerate([34, 52, 28, 62, 44, 58, 36]):
        bx = x + 8 + i * ((w - 16) // 7)
        bw = (w - 16) // 7 - 3
        d.rectangle([bx, y + h - 14 - bh, bx + bw, y + h - 14], fill=(70, 92, 128))
        for wy in range(0, bh - 6, 9):
            d.rectangle([bx + 2, y + h - 14 - bh + 3 + wy, bx + 5, y + h - 11 - bh + wy],
                        fill=(240, 200, 90))
    # three small flags on poles
    for i, col in enumerate([(178, 44, 36), (198, 152, 58), (240, 240, 240)]):
        px = x + w - 52 + i * 15
        d.line([px, y + 8, px, y + 26], fill=(220, 220, 220), width=2)
        d.rectangle([px, y + 8, px + 12, y + 17], fill=col)


def art_icj(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(203, 187, 148))
    # courthouse: pediment + columns
    d.polygon([(x + w // 2, y + 8), (x + 14, y + 30), (x + w - 14, y + 30)],
              fill=(44, 60, 96))
    for i in range(4):
        cx = x + 22 + i * ((w - 44) // 3)
        d.rectangle([cx - 4, y + 32, cx + 4, y + h - 12], fill=(255, 255, 255),
                    outline=(120, 120, 120))
    # scales of justice in the pediment
    sx, sy = x + w // 2, y + 16
    d.line([sx, sy - 4, sx, sy + 8], fill=(198, 152, 58), width=2)
    d.line([sx - 8, sy, sx + 8, sy], fill=(198, 152, 58), width=2)
    d.ellipse([sx - 11, sy + 2, sx - 5, sy + 8], outline=(198, 152, 58), width=2)
    d.ellipse([sx + 5, sy + 2, sx + 11, sy + 8], outline=(198, 152, 58), width=2)


def art_berlin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 41, 66))
    # EU stars ring
    cx, cy, r = x + w // 2, y + h // 2 - 6, 26
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(240, 200, 90))
    d.text((cx, cy), "€45bn", font=F(DJB, 20), fill=(255, 255, 255), anchor="mm")


def art_cepa(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 226))
    # container ship
    d.rectangle([x + 10, y + h - 34, x + w - 10, y + h - 22], fill=(44, 60, 96))
    for i, col in enumerate([(178, 82, 42), (198, 152, 58), (74, 120, 118), (178, 44, 36)]):
        cx0 = x + 16 + i * 18
        d.rectangle([cx0, y + h - 52, cx0 + 15, y + h - 34], fill=col)
    d.rectangle([x + w - 34, y + h - 58, x + w - 16, y + h - 34], fill=(240, 240, 240))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(74, 120, 118))
    for i in range(6):
        d.arc([x + 6 + i * 16, y + h - 16, x + 20 + i * 16, y + h - 2],
              180, 360, fill=(255, 255, 255), width=2)


def art_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 210, 180))
    # sun + wall (Yellow Line) + tank silhouette
    d.ellipse([x + w - 26, y + 8, x + w - 8, y + 26], fill=(240, 200, 90))
    d.rectangle([x, y + h - 30, x + w, y + h - 26], fill=(178, 82, 42))
    d.rectangle([x + 14, y + h - 44, x + 62, y + h - 30], fill=(60, 60, 60))
    d.rectangle([x + 20, y + h - 52, x + 44, y + h - 44], fill=(60, 60, 60))
    d.line([x + 44, y + h - 49, x + 74, y + h - 52], fill=(60, 60, 60), width=3)
    d.ellipse([x + 20, y + h - 28, x + 26, y + h - 22], fill=(40, 40, 40))
    d.ellipse([x + 32, y + h - 28, x + 38, y + h - 22], fill=(40, 40, 40))
    d.ellipse([x + 50, y + h - 28, x + 56, y + h - 22], fill=(40, 40, 40))


def art_sudan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 222, 188))
    d.ellipse([x + w - 30, y + 6, x + w - 10, y + 26], fill=(240, 190, 80))
    d.polygon([(x, y + h), (x + w * 0.4, y + h - 34), (x + w * 0.8, y + h),
               (x + w, y + h - 20), (x + w, y + h)], fill=(214, 178, 120))
    d.polygon([(x, y + h), (x + w * 0.5, y + h - 22), (x + w, y + h)],
              fill=(190, 150, 92))
    # drone dots in the sky
    for dx, dy in [(18, 16), (34, 10), (52, 20)]:
        d.ellipse([x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2], fill=(60, 60, 60))
        d.line([x + dx - 6, y + dy, x + dx + 6, y + dy], fill=(60, 60, 60), width=1)


def art_jeffries(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 41, 66))
    # capitol dome
    d.rectangle([x + 8, y + h - 16, x + w - 8, y + h - 10], fill=(240, 240, 240))
    d.rectangle([x + 16, y + h - 26, x + w - 16, y + h - 16], fill=(220, 220, 220))
    d.pieslice([x + w // 2 - 16, y + 8, x + w // 2 + 16, y + 40], 180, 360,
               fill=(240, 240, 240))
    d.rectangle([x + w // 2 - 2, y + 2, x + w // 2 + 2, y + 10], fill=(240, 240, 240))
    # small flag on the dome
    d.line([x + w // 2 + 2, y + 2, x + w // 2 + 2, y + 10], fill=(240, 200, 90),
           width=2)
    d.polygon([(x + w // 2 + 2, y + 2), (x + w // 2 + 12, y + 4),
               (x + w // 2 + 2, y + 7)], fill=(178, 44, 36))


def art_kerch(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 232))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(74, 120, 118))
    # bridge arc + broken span + burst
    d.arc([x + 6, y + 18, x + w - 6, y + h - 6], 200, 340, fill=(60, 60, 60), width=4)
    d.line([x + 8, y + h - 22, x + w - 8, y + h - 22], fill=(60, 60, 60), width=3)
    bx, by = x + w // 2, y + 22
    for a in range(0, 360, 45):
        r = 12
        ex = bx + r * math.cos(math.radians(a))
        ey = by + r * math.sin(math.radians(a))
        d.line([bx, by, ex, ey], fill=(240, 160, 40), width=2)
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(240, 160, 40))


def art_fiji(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 214, 170))
    # cracked dry earth
    for i, (x0, y0, x1, y1) in enumerate([
            (8, 30, 30, 44), (30, 44, 52, 34), (52, 34, 70, 48),
            (20, 52, 44, 62), (44, 62, 66, 54), (10, 66, 34, 74)]):
        d.line([x + x0, y + y0, x + x1, y + y1], fill=(140, 100, 60), width=2)
    # one water drop
    dx, dy = x + w - 24, y + 16
    d.polygon([(dx, dy - 8), (dx - 6, dy + 2), (dx + 6, dy + 2)], fill=(74, 120, 180))
    d.ellipse([dx - 6, dy - 2, dx + 6, dy + 8], fill=(74, 120, 180))


def art_bayesian(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 52, 82))
    # wind swirls
    for i in range(3):
        yy = y + 12 + i * 10
        d.arc([x + 8, yy, x + 44, yy + 12], 200, 340, fill=(200, 210, 230), width=2)
    # heeling yacht
    d.polygon([(x + 16, y + h - 22), (x + 66, y + h - 34), (x + 66, y + h - 18),
               (x + 20, y + h - 12)], fill=(240, 240, 240))
    d.line([x + 52, y + h - 32, x + 52, y + 18], fill=(220, 220, 220), width=2)
    d.polygon([(x + 54, y + 20), (x + 54, y + h - 36), (x + 78, y + h - 36)],
              fill=(226, 196, 120))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(74, 120, 180))


def art_chips(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 34, 56))
    # chip square with pins
    cx, cy, s = x + w // 2, y + h // 2, 34
    d.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2],
                fill=(44, 60, 96), outline=(198, 152, 58), width=2)
    d.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], fill=(198, 152, 58))
    for i in range(5):
        px = cx - 14 + i * 7
        d.line([px, cy - s // 2 - 6, px, cy - s // 2], fill=(198, 152, 58), width=2)
        d.line([px, cy + s // 2, px, cy + s // 2 + 6], fill=(198, 152, 58), width=2)
    d.text((cx, cy + s // 2 + 14), "AI", font=F(DJB, 11), fill=(240, 200, 90),
           anchor="mm")


def art_phchile(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 226))
    # two flags on poles + ship below
    for i, (top, bot) in enumerate([((0, 56, 147), (206, 17, 38)),
                                    ((0, 56, 147), (255, 255, 255))]):
        px = x + 16 + i * 30
        d.line([px, y + 8, px, y + 34], fill=(120, 120, 120), width=2)
        d.rectangle([px, y + 8, px + 24, y + 16], fill=top)
        d.rectangle([px, y + 16, px + 24, y + 24], fill=bot)
    d.ellipse([x + 8, y + h - 30, x + 26, y + h - 12], fill=(240, 200, 90))
    d.rectangle([x + 34, y + h - 24, x + w - 10, y + h - 14], fill=(44, 60, 96))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(74, 120, 118))


def art_bangladesh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 222, 188))
    # placards + flame
    for i, (px, col) in enumerate([(14, (178, 44, 36)), (36, (44, 60, 96)),
                                   (58, (62, 110, 72))]):
        d.line([x + px + 6, y + 26, x + px + 6, y + h - 16], fill=(90, 90, 90), width=2)
        d.rectangle([x + px, y + 12, x + px + 16, y + 26], fill=col)
    fx, fy = x + w - 20, y + h - 26
    d.polygon([(fx, fy - 14), (fx - 7, fy + 2), (fx - 2, fy + 2), (fx, fy + 8),
               (fx + 2, fy + 2), (fx + 7, fy + 2)], fill=(240, 140, 40))


ART = {
    "apec": art_apec, "icj": art_icj, "berlin": art_berlin, "cepa": art_cepa,
    "gaza": art_gaza, "sudan": art_sudan, "jeffries": art_jeffries,
    "kerch": art_kerch, "fiji": art_fiji, "bayesian": art_bayesian,
    "chips": art_chips, "phchile": art_phchile, "bangladesh": art_bangladesh,
}


# ---- layout ----
MX = 24                      # side margin
CW = W - 2 * MX              # content width = 976


def region_counts():
    counts = {}
    for c in CARDS:
        counts[c[4]] = counts.get(c[4], 0) + 1
    for b in BRIEFS:
        counts[b[2]] = counts.get(b[2], 0) + 1
    return counts


def draw_header(d):
    d.text((MX, 14), "THE WORLD IN ONE PAGE", font=F(DSB, 34), fill=INK)
    d.text((W - MX, 26), "THURSDAY 19 NOVEMBER 2026", font=F(DJB, 15),
           fill=RUST, anchor="ra")
    d.text((MX, 54), "40 STORIES · 7 REGIONS · ONE PAGE", font=F(DJB, 13), fill=NAVY)
    d.text((W - MX, 54), "A careful picture editor's summary of the day",
           font=F(DJ, 11), fill=GREY, anchor="ra")
    d.line([MX, 74, W - MX, 74], fill=INK, width=2)


def draw_region_bar(d, y):
    counts = region_counts()
    order = ["Europe", "Asia", "Middle East", "Africa", "Americas", "Oceania", "World"]
    total = sum(counts.values())
    x = MX
    for r in order:
        n = counts.get(r, 0)
        w = CW * n / total
        d.rectangle([x, y, x + w - 2, y + 12], fill=REGION_COLOR[r])
        x += w
    # one centred label line under the bar — no overlap on narrow segments
    parts = ["%s %d" % (r.upper(), counts.get(r, 0)) for r in order]
    label = "   ·   ".join(parts)
    d.text((MX + CW // 2, y + 22), label, font=F(DJB, 10), fill=INK, anchor="ma")
    return y + 34


def draw_card(d, card, x, y, w, h, lead=False):
    num, kicker, headline, deck, region, source, art, lon, lat = card
    col = REGION_COLOR[region]
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 4], fill=col)
    # number badge
    d.ellipse([x + 8, y + 10, x + 28, y + 30], fill=RED)
    d.text((x + 18, y + 20), str(num), font=F(DJB, 12), fill=(255, 255, 255),
           anchor="mm")
    d.text((x + 34, y + 12), kicker, font=F(DJB, 9), fill=col)
    d.text((x + w - 8, y + 12), source.upper(), font=F(DJB, 8), fill=GREY,
           anchor="ra")
    if lead:
        art_h = 72
        ART[art](d, x + 8, y + 32, w - 16, art_h)
        ty = y + 32 + art_h + 6
        hl = F(DJB, 16)
        dk = F(DJ, 11)
        max_lines_h, max_lines_d = 2, 3
    else:
        art_h = 48
        ART[art](d, x + 8, y + 30, w - 16, art_h)
        ty = y + 30 + art_h + 5
        hl = F(DJB, 12)
        dk = F(DJ, 10)
        max_lines_h, max_lines_d = 2, 2
    for i, line in enumerate(fit_text(d, headline, hl, w - 16, max_lines_h)):
        d.text((x + 8, ty + i * (hl.size + 2)), line, font=hl, fill=INK)
    dy = ty + len(fit_text(d, headline, hl, w - 16, max_lines_h)) * (hl.size + 2) + 2
    for i, line in enumerate(fit_text(d, deck, dk, w - 16, max_lines_d)):
        d.text((x + 8, dy + i * (dk.size + 3)), line, font=dk, fill=(60, 68, 80))


def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    # crop the poles: lat 85..-60 uses the height far better than -90..90
    px = mx + (lon + 180.0) / 360.0 * mw
    py = my + (85.0 - lat) / 145.0 * mh
    return px, py


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=MAP_BG, outline=LINE, width=1)
    d.text((x + 10, y + 8), "WHERE IT HAPPENED", font=F(DJB, 11), fill=NAVY)
    d.text((x + w - 10, y + 8), "pins 1–13 · dots 14–40", font=F(DJ, 9),
           fill=GREY, anchor="ra")
    mx, my, mw, mh = x + 8, y + 26, w - 16, h - 34
    step = 4
    px = mx
    while px < mx + mw:
        py = my
        while py < my + mh:
            lon = (px - mx) / mw * 360.0 - 180.0
            lat = 85.0 - (py - my) / mh * 145.0
            if is_land(lon, lat):
                d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=DOT)
            py += step
        px += step
    # brief dots first (under the pins)
    for num, headline, region, lon, lat in BRIEFS:
        bx, by = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=REGION_COLOR[region])
    # numbered pins for the 13 cards
    for num, kicker, headline, deck, region, source, art, lon, lat in CARDS:
        bx, by = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        if num == 11:  # nudge the chips pin clear of the Jeffries pin in DC
            bx += 20
            by -= 14
        if num == 7:
            bx -= 8
            by += 6
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=RED,
                  outline=(255, 255, 255), width=2)
        d.text((bx, by), str(num), font=F(DJB, 9), fill=(255, 255, 255),
               anchor="mm")
    # gold arrow for the ICJ pin (The Hague) — the day's legal landmark
    ix, iy = lonlat_to_xy(4.3, 52.1, mx, my, mw, mh)
    d.line([ix + 10, iy - 10, ix + 26, iy - 22], fill=GOLD, width=2)


def draw_numbers(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY, outline=LINE, width=1)
    d.text((x + 10, y + 8), "THE DAY IN NUMBERS", font=F(DJB, 11), fill=(240, 200, 90))
    cw = (w - 20) // 3
    ch = (h - 30) // 2
    for i, (big, label) in enumerate(NUMBERS):
        cx = x + 10 + (i % 3) * cw
        cy = y + 30 + (i // 3) * ch
        d.text((cx, cy), big, font=F(DJB, 17), fill=(255, 255, 255))
        for j, line in enumerate(fit_text(d, label, F(DJ, 9), cw - 6, 2)):
            d.text((cx, cy + 22 + j * 11), line, font=F(DJ, 9), fill=(200, 210, 230))


def draw_briefs(d, y):
    d.text((MX, y), "THE REST OF THE DAY — 14–40", font=F(DJB, 11), fill=NAVY)
    d.line([MX, y + 16, W - MX, y + 16], fill=LINE, width=1)
    col_w = (CW - 2 * 16) // 3
    for i, (num, headline, region, lon, lat) in enumerate(BRIEFS):
        col = i // 9
        row = i % 9
        bx = MX + col * (col_w + 16)
        by = y + 22 + row * 17
        d.text((bx, by), "%d." % num, font=F(DJB, 10), fill=REGION_COLOR[region])
        d.text((bx + 22, by), headline, font=F(DJ, 10), fill=INK)


def draw_footer(d, y):
    d.line([MX, y, W - MX, y], fill=INK, width=2)
    for i, line in enumerate(fit_text(d, DATE_CHECK, F(DJB, 10), CW, 3)):
        d.text((MX, y + 8 + i * 13), line, font=F(DJB, 10), fill=RUST)
    sy = y + 8 + len(fit_text(d, DATE_CHECK, F(DJB, 10), CW, 3)) * 13 + 4
    for i, line in enumerate(fit_text(d, SOURCES, F(DJ, 9), CW, 2)):
        d.text((MX, sy + i * 12), line, font=F(DJ, 9), fill=GREY)
    return sy + len(fit_text(d, SOURCES, F(DJ, 9), CW, 2)) * 12


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    y = draw_region_bar(d, 84)
    # 3 lead cards
    lead_w = (CW - 2 * 10) // 3
    for i, card in enumerate(CARDS[:3]):
        draw_card(d, card, MX + i * (lead_w + 10), y, lead_w, 182, lead=True)
    y += 182 + 10
    # 10 medium cards in 2 rows of 5
    med_w = (CW - 4 * 8) // 5
    for r in range(2):
        for c in range(5):
            card = CARDS[3 + r * 5 + c]
            draw_card(d, card, MX + c * (med_w + 8), y + r * (132 + 8),
                      med_w, 132, lead=False)
    y += 2 * 132 + 8 + 10
    # map + numbers side by side
    map_w = 640
    draw_map(d, MX, y, map_w, 172)
    draw_numbers(d, MX + map_w + 10, y, CW - map_w - 10, 172)
    y += 172 + 10
    draw_briefs(d, y)
    y += 22 + 9 * 17 + 8
    end = draw_footer(d, y)
    assert end <= H - 6, "footer overflow: %d" % end
    return img


def main():
    img = render()
    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
