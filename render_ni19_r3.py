#!/usr/bin/env python3
"""news-image-20261119 round 3 — "The World in One Page".

Renders entry.png (1024x1024) from the 40 verified 19-Nov 2026 stories
(same verified story list as round 2). Design follows the winning
news-image-20261118 round-5 formula: 3 illustrated leads + 10 medium
cards + briefs 14-40 + dotted world map with numbered pins +
day-in-numbers strip + region bar + DATE CHECK footer.

Differences vs round 2 (all genuine improvements, same stories):
- dotted map drawn from REAL Natural Earth 110m land polygons shipped
  in this repo (map_land.geojson), not a hand-written land mask;
- all 13 illustrations redrawn with Pillow primitives (no AI art);
- region counts shown as a proportional segmented bar, not just text;
- Liberation Serif display type + Liberation Sans body (newspaper face);
- map_land.geojson is committed, so the render is fully self-contained.

No network, no clock, no randomness — two runs are byte-identical.
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF_B = lambda s: font(f"{FL}/LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font(f"{FL}/LiberationSerif-Regular.ttf", s)
SERIF_I = lambda s: font(f"{FL}/LiberationSerif-Italic.ttf", s)
SANS = lambda s: font(f"{FL}/LiberationSans-Regular.ttf", s)
SANS_B = lambda s: font(f"{FL}/LiberationSans-Bold.ttf", s)
MONO_B = lambda s: font(f"{FD}/DejaVuSansMono-Bold.ttf", s)

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)      # warm newsprint
CARD = (255, 253, 247)       # card paper
INK = (22, 35, 58)           # navy ink
RUST = (179, 64, 42)         # accent rust
GREY = (107, 107, 102)
LINE = (216, 210, 194)       # hairline
NAVY_PANEL = (22, 35, 58)
NUM_LABEL = (174, 185, 204)
MAP_DOT = (143, 160, 184)
PIN = (179, 40, 28)

REGION_COLOR = {
    "Europe": (31, 58, 95),
    "Asia": (179, 64, 42),
    "Middle East": (122, 106, 47),
    "Africa": (183, 121, 31),
    "Americas": (46, 125, 107),
    "Oceania": (107, 78, 142),
    "World": (90, 90, 90),
}

# ------------------------------------------------------------- story data
# (num, region, kicker, source, headline, deck, art key)
CARDS = [
    (1, "Asia", "APEC · SHENZHEN", "REUTERS",
     "Three leaders, one table",
     "Trump, Xi and Putin hold the first trilateral of sitting US, "
     "Chinese and Russian presidents — one hour at Kylin Villa, "
     "nuclear arms on the agenda.", "apec"),
    (2, "World", "THE HAGUE · LAW", "ICJ / REUTERS",
     "Myanmar guilty of genocide",
     "ICJ rules 9–6: Myanmar committed genocide against the Rohingya "
     "in 2017 — the first time the court has found a state guilty. "
     "Reparations ordered.", "hague"),
    (3, "Europe", "BERLIN · UKRAINE", "REUTERS",
     "Europe demands a seat — and €45bn",
     "The Coalition of the Willing meets in Berlin pressing for "
     "binding security guarantees. The Commission proposes a €45bn "
     "loan for Ukraine in 2027.", "berlin"),
    (4, "Europe", "TRADE", "EU COUNCIL",
     "EU–Indonesia deal sealed",
     "EU Council authorises signature; signing 21 Nov. "
     "90% duty-free.", "trade"),
    (5, "Middle East", "GAZA", "DPA / REUTERS",
     "Tanks cross the Yellow Line",
     "First major ground op since the Oct 2025 ceasefire; "
     "three killed.", "gaza"),
    (6, "Africa", "SUDAN", "AMNESTY INTL",
     "Drones over El Obeid: 37 dead",
     "Amnesty: nine RSF drone strikes on El Obeid killed "
     "37 civilians.", "sudan"),
    (7, "Americas", "WASHINGTON", "REUTERS / AP",
     "Jeffries: history next",
     "Democrats nominate him 251–11; first Black speaker "
     "if elected.", "capitol"),
    (8, "Europe", "CRIMEA", "REUTERS",
     "Kerch hit a third time in a week",
     "Third strike in a week halts trains hours before "
     "the trilateral.", "kerch"),
    (9, "Oceania", "FIJI", "REUTERS",
     "A nation out of water",
     "One-month disaster declared; FJ$20m for "
     "emergency water.", "fiji"),
    (10, "Europe", "SICILY", "MAIB / GUARDIAN",
     "The wind nobody forecast",
     "MAIB: a ~70-knot downburst sank her in under "
     "15 seconds.", "yacht"),
    (11, "Americas", "CHIPS", "USCC / REUTERS",
     "China chases Nvidia's top chips",
     "PLA seeks Nvidia's top AI chips despite "
     "export curbs.", "chip"),
    (12, "Asia", "APEC", "INQUIRER",
     "Philippines–Chile: first LatAm deal",
     "Manila signs its first free-trade deal with "
     "Latin America.", "flags"),
    (13, "Asia", "BANGLADESH", "BSS / FE",
     "Homes of ex-MPs torched",
     "Awami League supporters torch ex-MPs' homes "
     "and a bank.", "fire"),
]

# briefs 14-40: short titles, one line each (verified 19-Nov stories)
BRIEFS = [
    "Gaza peace plan scores 4/26 one year on",
    "Gulf: Iran claims self-defence; US carrier pulls out",
    "Israel moves to repeal Netanyahu court overhaul",
    "Sudan blames Ethiopia and UAE for drone attacks",
    "WFP: month of food aid for 30,000 at El Dabba",
    "Ex-Sudan official wanted by ICC arrested",
    "Sudan army retakes Iyal Bakhit, downs RSF drone",
    "Tanzania's Samia in Uganda for Museveni talks",
    "Trump: Blackwell chips to China in '2–3 years'",
    "Congress drafts three bills to curb chip sales",
    "Nvidia stock 37% off its high after earnings",
    "Dutch watchdog: don't buy AI smart glasses",
    "Denmark to ratify Trump deal over Greenland",
    "Markets: DAX +0.8%, CAC +0.6%; UK near 6-week low",
    "Seoul's Lee renews call for talks with Pyongyang",
    "Korea–China trade deal raises hopes in Seoul",
    "Korea's big exam held under strict anti-cheat curbs",
    "Indonesia passes asset-forfeiture bill into law",
    "Singapore: don't split Asia-Pacific into blocs",
    "Japan's Takaichi: Taiwan stance unchanged",
    "IAEA: North Korea uranium enrichment expanding",
    "Women's Asian hockey trophy opens in Bhopal",
    "BTS to tour Asia and Australia from Kaohsiung",
    "Trump, Marcos hail alliance, pledge trade ties",
    "Myanmar's leader reconsiders ASEAN ties",
    "Anthropic's $81.3bn IPO arms AI price war",
    "COP31 climate summit opens in Antalya",
]

# (value, label) for the day-in-numbers panel
NUMBERS = [
    ("251–11", "Jeffries nominated"),
    ("€45bn", "EU loan for Ukraine"),
    ("9–6", "ICJ genocide vote"),
    ("$81.3bn", "Anthropic IPO"),
    ("37", "killed in El Obeid"),
    ("1,662", "Gaza dead since ceasefire"),
]

REGION_COUNTS = [
    ("Europe", 7), ("Asia", 14), ("Middle East", 4), ("Africa", 6),
    ("Americas", 5), ("Oceania", 1), ("World", 3),
]

# pins: story num -> (lon, lat) of the place it happened
PINS = {
    1: (114.06, 22.55),    # Shenzhen
    2: (4.30, 52.07),      # The Hague
    3: (13.40, 52.52),     # Berlin
    4: (4.35, 50.85),      # Brussels
    5: (34.45, 31.45),     # Gaza / Bureij
    6: (30.22, 13.18),     # El Obeid
    7: (-77.04, 38.90),    # Washington DC
    8: (36.47, 45.35),     # Kerch
    9: (178.44, -18.14),   # Suva, Fiji
    10: (13.53, 38.08),    # Porticello, Sicily
    11: (116.40, 39.90),   # Beijing
    12: (120.98, 14.60),   # Manila
    13: (89.82, 23.00),    # Gopalganj, Bangladesh
}
# manual nudge (dx, dy) in px for pins that would overlap on the map
PIN_NUDGE = {1: (-14, 4), 2: (-14, -8), 3: (18, -10), 4: (-16, 12),
             5: (-12, -8), 6: (10, 12), 8: (16, 6), 10: (14, 16),
             11: (12, -10), 12: (14, 10)}

DATE_CHECK = (
    "DATE CHECK — Left out on purpose, first reported Tue 17 Nov: "
    "Kerch road-span collapse · Nvidia's $115.8bn quarter · Peltola's "
    "Alaska Senate win · Mongolia president's resignation announced · "
    "Prague train crash · Knesset speaker vote · Waymo freeway pause · "
    "Russian jets breach Japan's airspace."
)
SOURCES = (
    "Sources: Reuters · AP · AFP · BBC · Al Jazeera · EU Council · ICJ · "
    "MAIB · Amnesty International · USCC · Inquirer · BSS · The Guardian. "
    "Every story verified against wire coverage of 19 Nov 2026."
)


# ---------------------------------------------------------------- helpers
def wrap(text, fnt, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_lines(d, x, y, lines, fnt, fill, lh):
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def rrect(d, box, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline,
                        width=width)


def card_frame(d, x, y, w, h, region):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 4], fill=REGION_COLOR[region])


def badge(d, cx, cy, n, r=10):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PIN)
    f = SANS_B(11 if r >= 10 else 10)
    t = str(n)
    tw = f.getlength(t)
    d.text((cx - tw / 2, cy - 7), t, font=f, fill=(255, 255, 255))


def draw_card(d, x, y, w, h, c, art_fn, lead=False):
    num, region, kicker, source, headline, deck, _art = c
    card_frame(d, x, y, w, h, region)
    badge(d, x + 15, y + 15, num, r=10 if lead else 9)
    kf = SANS_B(11 if lead else 9)
    d.text((x + 30, y + 9), kicker, font=kf, fill=REGION_COLOR[region])
    sf = SANS(8 if lead else 7)
    sw = sf.getlength(source)
    d.text((x + w - 8 - sw, y + 10), source, font=sf, fill=GREY)
    ax, ay = x + 8, y + 28
    aw, ah = (w - 16, 88) if lead else (w - 14, 56)
    art_fn(d, ax, ay, aw, ah)
    hy = ay + ah + 6
    hf = SERIF_B(17 if lead else 14)
    hl = wrap(headline, hf, w - 16)
    hy = text_lines(d, x + 8, hy, hl, hf, INK, 19 if lead else 17)
    df = SANS(11 if lead else 10)
    dl = wrap(deck, df, w - 16)
    text_lines(d, x + 8, hy + 2, dl, df, (58, 58, 54), 13 if lead else 12)

# ---------------------------------------------------------------- art
# Every panel is drawn with Pillow primitives only. Panels are small
# (leads 300x88, mediums 172x56), so each scene is a few bold shapes.

def art_apec(d, x, y, w, h):
    # dusk sky, skyline, three flags, low sun
    d.rectangle([x, y, x + w, y + h], fill=(24, 42, 74))
    d.ellipse([x + w - 52, y + 8, x + w - 22, y + 38], fill=(232, 178, 74))
    base = y + h
    for bx, bw, bh in [(0, 34, 46), (38, 26, 62), (68, 30, 38),
                       (102, 24, 70), (130, 34, 50), (168, 26, 64),
                       (198, 30, 42), (232, 34, 58), (270, 30, 48)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base],
                    fill=(13, 26, 50))
        for wy in range(base - bh + 8, base - 6, 12):
            d.rectangle([x + bx + 6, wy, x + bx + 12, wy + 5],
                        fill=(232, 178, 74))
    d.rectangle([x, base - 6, x + w, base], fill=(13, 26, 50))
    for i, col in enumerate([(178, 34, 34), (255, 222, 0), (31, 58, 95)]):
        fx = x + 12 + i * 16
        d.line([fx, y + 12, fx, y + 30], fill=(230, 230, 220), width=2)
        d.polygon([(fx, y + 12), (fx + 12, y + 16), (fx, y + 20)],
                  fill=col)


def art_hague(d, x, y, w, h):
    # courthouse pediment + columns + scales of justice
    d.rectangle([x, y, x + w, y + h], fill=(233, 226, 205))
    d.polygon([(x + 10, y + 34), (x + w // 2, y + 8), (x + w - 10, y + 34)],
              fill=(31, 58, 95))
    d.ellipse([x + w // 2 - 4, y + 16, x + w // 2 + 4, y + 24],
              fill=(232, 178, 74))
    for cx in [x + 26, x + w // 2 - 52, x + w // 2 + 44, x + w - 34]:
        d.rectangle([cx, y + 36, cx + 8, y + h - 12], fill=(250, 248, 240))
    d.rectangle([x + 8, y + h - 12, x + w - 8, y + h - 6],
                fill=(31, 58, 95))
    # scales
    sx, sy = x + w - 34, y + 44
    d.line([sx, sy, sx, sy + 12], fill=(120, 96, 40), width=2)
    d.line([sx - 10, sy + 2, sx + 10, sy + 2], fill=(120, 96, 40), width=2)
    d.arc([sx - 12, sy + 8, sx - 4, sy + 16], 0, 180, fill=(120, 96, 40))
    d.arc([sx + 4, sy + 8, sx + 12, sy + 16], 0, 180, fill=(120, 96, 40))


def art_berlin(d, x, y, w, h):
    # navy night, ring of EU stars, big gold figure
    d.rectangle([x, y, x + w, y + h], fill=(16, 28, 54))
    cx, cy, r = x + w // 2, y + h // 2, 34
    import math
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(232, 178, 74))
    f = SERIF_B(30)
    t = "€45bn"
    d.text((cx - f.getlength(t) / 2, cy - 16), t, font=f,
           fill=(240, 196, 90))


def art_trade(d, x, y, w, h):
    # container ship on waves
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 236))
    d.rectangle([x, y, x + w, y + 14], fill=(178, 203, 218))
    d.ellipse([x + w - 34, y + 2, x + w - 14, y + 22], fill=(240, 220, 150))
    hull_y = y + h - 18
    d.polygon([(x + 8, hull_y), (x + w - 8, hull_y),
               (x + w - 22, y + h - 4), (x + 22, y + h - 4)],
              fill=(31, 58, 95))
    for i, col in enumerate([(179, 64, 42), (46, 125, 107), (183, 121, 31),
                             (31, 58, 95), (179, 64, 42)]):
        d.rectangle([x + 16 + i * 30, hull_y - 16, x + 42 + i * 30, hull_y],
                    fill=col)
    for wx in range(0, w, 26):
        d.arc([x + wx, y + h - 10, x + wx + 22, y + h + 2], 180, 360,
              fill=(31, 58, 95))


def art_gaza(d, x, y, w, h):
    # desert, tank silhouette, dashed yellow line
    d.rectangle([x, y, x + w, y + h], fill=(226, 205, 158))
    d.ellipse([x + w - 30, y + 6, x + w - 10, y + 26], fill=(240, 200, 90))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(198, 168, 112))
    tx, ty = x + w // 2 - 34, y + h - 34
    d.rectangle([tx, ty, tx + 58, ty + 12], fill=(58, 52, 44))
    d.rectangle([tx + 14, ty - 10, tx + 40, ty], fill=(58, 52, 44))
    d.line([tx + 40, ty - 6, tx + 68, ty - 6], fill=(58, 52, 44), width=3)
    for wx in range(tx - 4, tx + 64, 10):
        d.ellipse([wx, ty + 12, wx + 6, ty + 18], fill=(40, 36, 30))
    for lx in range(x + 8, x + w - 8, 14):
        d.line([lx, y + 8, lx + 8, y + 8], fill=(232, 178, 74), width=3)


def art_sudan(d, x, y, w, h):
    # pale sky, sun, three drones with motion lines
    d.rectangle([x, y, x + w, y + h], fill=(238, 226, 196))
    d.ellipse([x + w - 36, y + 4, x + w - 12, y + 28], fill=(240, 190, 80))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(214, 186, 138))
    for i, (dx, dy) in enumerate([(18, 12), (72, 26), (122, 10)]):
        px, py = x + dx, y + dy
        d.line([px - 9, py, px + 9, py], fill=(40, 40, 36), width=2)
        d.line([px, py - 3, px, py + 5], fill=(40, 40, 36), width=2)
        d.ellipse([px - 11, py - 2, px - 5, py + 2], fill=(120, 120, 116))
        d.ellipse([px + 5, py - 2, px + 11, py + 2], fill=(120, 120, 116))
        d.line([px - 22, py + 10, px - 12, py + 10], fill=(160, 150, 130),
               width=1)


def art_capitol(d, x, y, w, h):
    # capitol dome on pale blue, tally strip
    d.rectangle([x, y, x + w, y + h], fill=(212, 222, 234))
    cx = x + w // 2
    d.rectangle([x + 14, y + h - 14, x + w - 14, y + h - 6],
                fill=(250, 248, 240))
    d.polygon([(cx - 26, y + h - 14), (cx + 26, y + h - 14),
               (cx + 18, y + 22), (cx - 18, y + 22)], fill=(250, 248, 240))
    d.pieslice([cx - 20, y + 2, cx + 20, y + 34], 180, 360,
               fill=(250, 248, 240))
    d.line([cx, y + 2, cx, y - 2], fill=(31, 58, 95), width=2)
    d.ellipse([cx - 2, y - 4, cx + 2, y], fill=(31, 58, 95))


def art_kerch(d, x, y, w, h):
    # strait, bridge deck with a gap, smoke, blast star
    d.rectangle([x, y, x + w, y + h], fill=(168, 196, 210))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(120, 158, 178))
    gy = y + 22
    d.rectangle([x, gy, x + w // 2 - 14, gy + 6], fill=(52, 52, 48))
    d.rectangle([x + w // 2 + 14, gy, x + w, gy + 6], fill=(52, 52, 48))
    for px in [x + 30, x + w - 40]:
        d.rectangle([px, gy + 6, px + 5, y + h - 14], fill=(52, 52, 48))
    bx, by = x + w // 2, gy - 4
    for dx, dy, r, col in [(-8, -8, 7, (240, 200, 90)),
                           (4, -12, 9, (240, 150, 60)),
                           (0, -4, 6, (250, 230, 150))]:
        d.ellipse([bx + dx - r, by + dy - r, bx + dx + r, by + dy + r],
                  fill=col)
    d.ellipse([bx - 16, by - 26, bx - 2, by - 12], fill=(120, 120, 116))
    d.ellipse([bx + 2, by - 30, bx + 18, by - 14], fill=(140, 140, 136))


def art_fiji(d, x, y, w, h):
    # cracked dry earth, one blue drop
    d.rectangle([x, y, x + w, y + h], fill=(224, 200, 150))
    for (x1, y1, x2, y2) in [(8, 40, 40, 22), (40, 22, 70, 36),
                             (70, 36, 96, 20), (96, 20, 130, 34),
                             (130, 34, 164, 18), (30, 50, 60, 40),
                             (90, 50, 110, 38)]:
        d.line([x + x1, y + y1, x + x2, y + y2], fill=(140, 104, 62),
               width=2)
    d.polygon([(x + w - 26, y + 12), (x + w - 14, y + 28),
               (x + w - 38, y + 28)], fill=(52, 120, 180))
    d.ellipse([x + w - 34, y + 22, x + w - 18, y + 38], fill=(52, 120, 180))


def art_yacht(d, x, y, w, h):
    # night squall, heeled yacht
    d.rectangle([x, y, x + w, y + h], fill=(16, 32, 60))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(30, 58, 92))
    for rx in range(6, w, 18):
        d.line([x + rx, y + 6, x + rx - 8, y + 22], fill=(90, 120, 160),
               width=1)
    cx, cy = x + w // 2, y + h - 16
    d.polygon([(cx - 30, cy), (cx + 34, cy - 4), (cx + 30, cy + 8),
               (cx - 26, cy + 8)], fill=(250, 248, 240))
    d.line([cx + 6, cy - 4, cx - 8, y + 8], fill=(220, 220, 210), width=2)
    d.polygon([(cx + 2, cy - 4), (cx - 8, y + 10), (cx - 2, cy - 4)],
              fill=(240, 236, 220))
    d.ellipse([cx + 22, cy - 12, cx + 30, cy - 4], fill=(240, 200, 90))


def art_chip(d, x, y, w, h):
    # dark board, gold chip, circuit traces
    d.rectangle([x, y, x + w, y + h], fill=(18, 26, 44))
    for ty in [10, 26, 42]:
        d.line([x + 6, y + ty, x + 34, y + ty], fill=(90, 140, 110),
               width=1)
        d.line([x + w - 34, y + ty, x + w - 6, y + ty],
               fill=(90, 140, 110), width=1)
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 20, cy - 16, cx + 20, cy + 16], fill=(232, 178, 74))
    d.rectangle([cx - 11, cy - 8, cx + 11, cy + 8], fill=(180, 130, 40))
    for px in range(cx - 16, cx + 17, 8):
        d.line([px, cy - 22, px, cy - 16], fill=(200, 200, 190), width=2)
        d.line([px, cy + 16, px, cy + 22], fill=(200, 200, 190), width=2)


def art_flags(d, x, y, w, h):
    # two flags on poles over a globe arc
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 238))
    d.arc([x + 6, y + h - 8, x + w - 6, y + h + 26], 180, 360,
          fill=(120, 150, 180), width=3)
    for i, (top, bot) in enumerate([((52, 120, 200), (200, 60, 60)),
                                    ((200, 60, 60), (250, 248, 240))]):
        fx = x + 22 + i * 74
        d.line([fx, y + 10, fx, y + h - 14], fill=(90, 90, 86), width=2)
        d.rectangle([fx, y + 10, fx + 52, y + 24], fill=top)
        d.rectangle([fx, y + 24, fx + 52, y + 38], fill=bot)
        d.ellipse([fx + 20, y + 15, fx + 32, y + 27], fill=(240, 200, 90))


def art_fire(d, x, y, w, h):
    # dark buildings, flames, smoke
    d.rectangle([x, y, x + w, y + h], fill=(38, 34, 44))
    for bx, bw, bh in [(6, 34, 30), (46, 28, 40), (80, 34, 26),
                       (120, 30, 38)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                    fill=(24, 22, 32))
        for wy in range(y + h - bh + 6, y + h - 4, 10):
            d.rectangle([x + bx + 6, wy, x + bx + 12, wy + 5],
                        fill=(232, 178, 74))
    for fx, fh in [(28, 22), (62, 30), (100, 20), (136, 26)]:
        d.polygon([(x + fx - 8, y + h - 6), (x + fx, y + h - 6 - fh),
                   (x + fx + 8, y + h - 6), (x + fx + 3, y + h - 12),
                   (x + fx - 3, y + h - 12)], fill=(240, 140, 50))
        d.polygon([(x + fx - 4, y + h - 6), (x + fx, y + h - 6 - fh + 8),
                   (x + fx + 4, y + h - 6)], fill=(250, 210, 90))
    d.ellipse([x + 20, y + 4, x + 40, y + 18], fill=(110, 110, 116))
    d.ellipse([x + 90, y + 2, x + 112, y + 16], fill=(130, 130, 136))


ART = {
    "apec": art_apec, "hague": art_hague, "berlin": art_berlin,
    "trade": art_trade, "gaza": art_gaza, "sudan": art_sudan,
    "capitol": art_capitol, "kerch": art_kerch, "fiji": art_fiji,
    "yacht": art_yacht, "chip": art_chip, "flags": art_flags,
    "fire": art_fire,
}

# ---------------------------------------------------------------- map
def load_land():
    """Return [(bbox, [exterior, holes...]), ...] from map_land.geojson."""
    with open(os.path.join(HERE, "map_land.geojson")) as f:
        gj = json.load(f)
    polys = []
    for feat in gj["features"]:
        geom = feat["geometry"]
        geoms = []
        if geom["type"] == "Polygon":
            geoms = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            geoms = geom["coordinates"]
        for poly in geoms:
            rings = [list(map(tuple, ring)) for ring in poly]
            xs = [p[0] for ring in rings for p in ring]
            ys = [p[1] for ring in rings for p in ring]
            polys.append(((min(xs), min(ys), max(xs), max(ys)), rings))
    return polys


def _in_ring(lon, lat, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > lat) != (yj > lat):
            xinters = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xinters:
                inside = not inside
        j = i
    return inside


def _on_land(lon, lat, polys):
    for (x0, y0, x1, y1), rings in polys:
        if not (x0 <= lon <= x1 and y0 <= lat <= y1):
            continue
        if _in_ring(lon, lat, rings[0]):
            if any(_in_ring(lon, lat, hole) for hole in rings[1:]):
                continue
            return True
    return False


def draw_map(d, mx0, my0, mx1, my1, polys):
    """Dotted world map from real land polygons + numbered pins."""
    lon_step, lat_step = 2.2, 2.6
    lat_top, lat_bot = 82.0, -58.0
    row = 0
    lat = lat_top
    while lat > lat_bot:
        # stagger alternate rows by half a step (hex packing): breaks
        # the horizontal striping a square grid leaves behind
        lon = -179.0 + (lon_step / 2 if row % 2 else 0.0)
        while lon < 180.0:
            if _on_land(lon, lat, polys):
                px = mx0 + (lon + 180.0) / 360.0 * (mx1 - mx0)
                py = my0 + (lat_top - lat) / (lat_top - lat_bot) * (my1 - my0)
                d.ellipse([px - 1.4, py - 1.4, px + 1.4, py + 1.4],
                          fill=MAP_DOT)
            lon += lon_step
        lat -= lat_step
        row += 1
    for num, (plon, plat) in sorted(PINS.items()):
        px = mx0 + (plon + 180.0) / 360.0 * (mx1 - mx0)
        py = my0 + (lat_top - plat) / (lat_top - lat_bot) * (my1 - my0)
        dx, dy = PIN_NUDGE.get(num, (0, 0))
        if (dx, dy) != (0, 0):
            d.line([px, py, px + dx, py + dy], fill=PIN, width=1)
            px, py = px + dx, py + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=PIN,
                  outline=(255, 255, 255), width=1)
        f = SANS_B(9)
        t = str(num)
        d.text((px - f.getlength(t) / 2, py - 6), t, font=f,
               fill=(255, 255, 255))


# ---------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    polys = load_land()

    # masthead
    d.text((26, 14), "THE WORLD IN ONE PAGE", font=SERIF_B(46), fill=INK)
    df = SANS_B(15)
    dt = "THURSDAY 19 NOVEMBER 2026"
    d.text((998 - df.getlength(dt), 28), dt, font=df, fill=RUST)
    d.text((26, 68), "40 STORIES · 7 REGIONS · ONE PAGE", font=SANS_B(12),
           fill=INK)
    tag = "A careful picture editor's summary of the day"
    tf = SERIF_I(12)
    d.text((998 - tf.getlength(tag), 68), tag, font=tf, fill=GREY)
    d.rectangle([26, 90, 998, 93], fill=INK)
    d.rectangle([26, 95, 998, 96], fill=INK)

    # region bar: proportional segments + labelled counts
    bx, by, bw = 26, 100, 972
    total = sum(n for _, n in REGION_COUNTS)
    x = bx
    for name, n in REGION_COUNTS:
        seg = bw * n / total
        d.rectangle([x, by, x + seg, by + 10], fill=REGION_COLOR[name])
        x += seg
    labels = []
    lf = SANS_B(10)
    for name, n in REGION_COUNTS:
        labels.append((REGION_COLOR[name], f"{name.upper()} {n}"))
    lw = sum(9 + lf.getlength(t) + 14 for _, t in labels) - 14
    x = 26 + (972 - lw) / 2
    for col, t in labels:
        d.rectangle([x, 121, x + 7, 128], fill=col)
        d.text((x + 9, 118), t, font=lf, fill=INK)
        x += 9 + lf.getlength(t) + 14

    # lead row: 3 cards
    for i, c in enumerate(CARDS[:3]):
        draw_card(d, 26 + i * 328, 138, 316, 208, c,
                  ART[c[6]], lead=True)

    # medium rows: 5 + 5 cards
    xs = [26, 222, 418, 614, 810]
    for j, c in enumerate(CARDS[3:8]):
        draw_card(d, xs[j], 354, 186, 156, c, ART[c[6]])
    for j, c in enumerate(CARDS[8:13]):
        draw_card(d, xs[j], 518, 186, 156, c, ART[c[6]])

    # map + numbers band
    d.rectangle([26, 682, 660, 828], fill=CARD, outline=LINE, width=1)
    d.text((36, 690), "WHERE IT HAPPENED", font=SANS_B(11), fill=INK)
    d.text((560, 690), "pins 1–13", font=SANS(9), fill=GREY)
    draw_map(d, 34, 706, 652, 822, polys)

    d.rectangle([670, 682, 998, 828], fill=NAVY_PANEL)
    d.text((684, 690), "THE DAY IN NUMBERS", font=SANS_B(11),
           fill=(255, 255, 255))
    vf, lf2 = SERIF_B(21), SANS(9)
    for i, (val, lab) in enumerate(NUMBERS):
        col = i % 2
        row = i // 2
        vx = 684 + col * 164
        vy = 712 + row * 38
        d.text((vx, vy), val, font=vf, fill=(255, 255, 255))
        d.text((vx, vy + 23), lab, font=lf2, fill=NUM_LABEL)

    # briefs 14-40 in three columns
    d.text((26, 836), "THE REST OF THE DAY — 14–40", font=SANS_B(11),
           fill=INK)
    d.rectangle([26, 852, 998, 853], fill=LINE)
    bf, nf = SANS(9), SANS_B(9)
    col_x = [26, 354, 682]
    for k, title in enumerate(BRIEFS):
        col, row = k // 9, k % 9
        x = col_x[col]
        y = 858 + row * 13
        num = str(14 + k) + "."
        d.text((x, y), num, font=nf, fill=RUST)
        d.text((x + 22, y), title, font=bf, fill=(58, 58, 54))

    # footer
    dlf = SANS_B(10)
    dl = wrap(DATE_CHECK, dlf, 972)
    y = 978
    y = text_lines(d, 26, y, dl, dlf, RUST, 12)
    sl = wrap(SOURCES, SANS(8), 972)
    text_lines(d, 26, y + 2, sl, SANS(8), GREY, 11)

    return img


def main():
    img = render()
    img.save(os.path.join(HERE, "entry.png"), optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
