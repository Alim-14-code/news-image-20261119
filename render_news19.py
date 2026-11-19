#!/usr/bin/env python3
"""Render entry.png for make.fun news-image-20261119.

One page, Thursday 19 November 2026: 7 stories, 4 regions.
Written from scratch in this session. Layout follows the winning
news-image-20261118 R5 formula (leads + medium cards + dotted world
map with numbered pins + numbers strip + DATE CHECK footer), with
original text, original decks and original Pillow illustrations for
the three stories without AI art.

AI art (assets/): cards 1-4 are AI-generated scenes, used as card
art. Cards 5-7 are drawn here with Pillow primitives in the same
muted palette.

Deterministic: no network, no clock, no randomness at render time.
The dotted map reads Natural Earth 110m land polygons from
/tmp/ne_110m_land.geojson (downloaded in-session, not committed);
if that file is absent it falls back to a graticule-only map.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
GEOJSON = "/tmp/ne_110m_land.geojson"

W, H = 1024, 1024

# ---- muted palette (matches the AI card art) ----
PAPER = (245, 240, 230)
CARD = (255, 255, 255)
INK = (28, 39, 51)
NAVY = (31, 42, 68)
NAVY2 = (42, 58, 92)
RUST = (180, 85, 45)
TEAL = (78, 122, 120)
TEAL_DK = (38, 74, 76)
SAND = (228, 217, 195)
SAND_DK = (201, 185, 146)
GOLD = (199, 154, 59)
GOLD_LT = (226, 196, 120)
GREY = (107, 114, 128)
LINE = (216, 207, 187)
DOT = (122, 139, 155)
MAP_BG = (238, 233, 220)

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DSB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


# ---- the day's stories (verified 19 Nov 2026, see briefs.md) ----
# image: None -> drawn with Pillow; otherwise an asset filename.
STORIES = [
    dict(
        n=1, region="ASIA", pin=(114.05, 22.55),
        image="media-generation-card-apec-0-915050dd-36ca-4ab6-a9d3-3f2c16027020.png",
        head="THREE LEADERS, ONE TABLE",
        deck=("Trump, Xi and Putin held the first trilateral of sitting US, "
              "Chinese and Russian presidents \u2014 one hour at Kylin Villa, "
              "Shenzhen, with nuclear arms on top of the agenda after New "
              "START expired in February. No deal was expected; Trump and "
              "Putin also met one-on-one, and Xi pledged $20M for APEC "
              "cooperation."),
        src="REUTERS \u00b7 AL JAZEERA \u2014 19 NOV",
    ),
    dict(
        n=2, region="EUROPE", pin=(4.35, 50.85),
        image="media-generation-card-eu-id-0-a2d6d861-b9c1-467d-aba9-fe8c0f7144b0.png",
        head="TRADE DEAL SEALED",
        deck=("The EU Council authorised signature of the CEPA deals; signing "
              "is expected 21 Nov. Over 90% of products go duty-free, 98.5% "
              "of tariff lines freed in full \u2014 about \u20ac600M a year."),
        src="AL JAZEERA \u00b7 EU COUNCIL \u2014 19 NOV",
    ),
    dict(
        n=3, region="EUROPE", pin=(13.40, 52.52),
        image="media-generation-card-berlin-0-ca780c8f-2735-4bdb-b63d-4487a829c93e.png",
        head="EUROPE DEMANDS A SEAT",
        deck=("The \u2018Coalition of the Willing\u2019 met in Berlin with NATO "
              "chief Rutte and Trump\u2019s envoys, pressing for binding "
              "security guarantees for Ukraine after any ceasefire."),
        src="REUTERS \u2014 19 NOV",
    ),
    dict(
        n=4, region="OCEANIA", pin=(178.0, -17.73),
        image="card-fiji.png",
        head="A NATION OUT OF WATER",
        deck=("Fiji declared a one-month state of disaster as El Ni\u00f1o "
              "drought empties reservoirs. PM Rabuka set aside FJ$20M for "
              "emergency water; below-normal rain is forecast until April."),
        src="REUTERS \u2014 19 NOV",
    ),
    dict(
        n=5, region="AMERICAS", pin=(-77.01, 38.89),
        image=None, art="jeffries",
        head="251\u201311: HISTORY NEXT",
        deck=("House Democrats nominated Hakeem Jeffries as speaker "
              "candidate in a 251\u201311 vote. If elected on the House floor "
              "on 3 Jan, he would be the first Black speaker."),
        src="REUTERS \u00b7 AP \u2014 19 NOV",
    ),
    dict(
        n=6, region="EUROPE", pin=(35.40, 45.30),
        image=None, art="bridge",
        head="THIRD STRIKE IN A WEEK",
        deck=("Ukraine hit the Crimean Bridge for the third time in a week, "
              "halting trains hours before the trilateral."),
        src="REUTERS \u2014 19 NOV",
    ),
    dict(
        n=7, region="EUROPE", pin=(13.53, 38.08),
        image=None, art="bayesian",
        head="THE WIND NOBODY FORECAST",
        deck=("The MAIB final report says the Bayesian had a hidden wind "
              "weakness \u2014 a ~70-knot downburst knocked her over in "
              "under 15 seconds."),
        src="THE GUARDIAN \u00b7 MAIB \u2014 19 NOV",
    ),
]

NUMBERS = [
    ("3 leaders", "first US\u2013China\u2013Russia trilateral"),
    ("98.5%", "tariff lines freed, EU\u2013Indonesia"),
    ("\u20ac600M / yr", "saved once CEPA is fully in force"),
    ("251\u201311", "Jeffries nominated for speaker"),
    ("FJ$20M", "Fiji drought response"),
    ("70 kt", "downburst that sank the Bayesian"),
]

DATE_CHECK = ("DATE CHECK \u2014 Deliberately left out: Waymo\u2019s freeway pause "
              "(first reported 17 Nov) \u00b7 Tuesday\u2019s Kerch road-span collapse "
              "(17 Nov) \u00b7 Nvidia\u2019s $115.8bn quarter (17 Nov). Every story "
              "above was reported 19 Nov.")
SOURCES = ("Sources: Reuters \u00b7 Al Jazeera \u00b7 The Guardian \u00b7 AP / AFP via "
           "The Standard \u00b7 MAIB \u00b7 EU Council \u2014 19 Nov 2026 (WIB). "
           "Images: AI-generated scenes (1\u20134) + original illustrations (5\u20137).")


# ---- text helpers ----
def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, text, font, fill, x, y, max_w, leading, max_lines=None):
    """Draw wrapped text; returns the y just below the last line drawn."""
    lines = wrap(draw, text, font, max_w)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        # ellipsis on the last line
        while lines and draw.textlength(lines[-1] + "\u2026", font=font) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "\u2026"
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def cover_fit(im, tw, th):
    """Centre-crop + resize to exactly tw x th."""
    w, h = im.size
    scale = max(tw / w, th / h)
    nw, nh = int(w * scale + 0.5), int(h * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return im.crop((x, y, x + tw, y + th))


def number_badge(draw, x, y, n, r=11):
    draw.ellipse([x - r, y - r, x + r, y + r], fill=RUST)
    draw.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255), width=2)
    f = F(DJB, 13)
    t = str(n)
    tw = draw.textlength(t, font=f)
    th = f.getbbox(t)[3]
    draw.text((x - tw / 2, y - th / 2 - 1), t, font=f, fill=(255, 255, 255))


# ---- Pillow illustrations (stories 5-7, same muted palette) ----
def art_jeffries(w, h):
    """Capitol dome + big 251, flat shapes on deep navy."""
    im = Image.new("RGB", (w, h), NAVY2)
    d = ImageDraw.Draw(im)
    # sky glow
    d.ellipse([w * 0.55, -h * 0.55, w * 1.25, h * 0.75], fill=(58, 76, 116))
    # capitol dome silhouette, right side
    cx, base = int(w * 0.78), int(h * 0.98)
    d.rectangle([cx - 52, base - 34, cx + 52, base], fill=(214, 206, 188))
    d.pieslice([cx - 40, base - 78, cx + 40, base - 6], 180, 360,
               fill=(232, 226, 210))
    d.rectangle([cx - 3, base - 92, cx + 3, base - 76], fill=(232, 226, 210))
    d.ellipse([cx - 5, base - 96, cx + 5, base - 88], fill=GOLD_LT)
    for i in range(-2, 3):
        d.rectangle([cx + i * 18 - 4, base - 32, cx + i * 18 + 4, base],
                    fill=NAVY2)
    d.rectangle([0, base - 2, w, h], fill=SAND_DK)
    # big vote tally, left side, below the number badge
    f_big = F(DJB, 44)
    d.text((14, int(h * 0.44)), "251", font=f_big, fill=GOLD_LT)
    f_sm = F(DJB, 15)
    d.text((16, int(h * 0.72)), "\u201311", font=f_sm, fill=(232, 226, 210))
    d.text((16, int(h * 0.86)), "DEMOCRATS", font=F(DJB, 10),
           fill=(168, 182, 200))
    return im


def art_bridge(w, h):
    """Bridge deck with a gap + smoke over a strait."""
    im = Image.new("RGB", (w, h), (233, 224, 205))
    d = ImageDraw.Draw(im)
    # sky + sea
    d.rectangle([0, 0, w, int(h * 0.52)], fill=(233, 224, 205))
    d.rectangle([0, int(h * 0.52), w, h], fill=(94, 128, 138))
    for i in range(5):
        yy = int(h * 0.60) + i * 9
        d.arc([-10, yy - 6, w + 10, yy + 10], 200, 340, fill=(150, 180, 188))
    # towers
    for tx in (int(w * 0.22), int(w * 0.72)):
        d.rectangle([tx - 3, int(h * 0.14), tx + 3, int(h * 0.52)],
                    fill=(70, 82, 100))
        d.line([tx, int(h * 0.14), int(w * 0.47), int(h * 0.50)],
               fill=(70, 82, 100), width=2)
        d.line([tx, int(h * 0.14), int(w * 0.02), int(h * 0.50)],
               fill=(70, 82, 100), width=2)
    # deck with a gap in the middle (the destroyed span)
    d.rectangle([0, int(h * 0.48), int(w * 0.42), int(h * 0.52)],
                fill=(52, 62, 78))
    d.rectangle([int(w * 0.58), int(h * 0.48), w, int(h * 0.52)],
                fill=(52, 62, 78))
    # smoke over the gap
    for (sx, sy, sr) in [(0.47, 0.30, 13), (0.52, 0.22, 17), (0.50, 0.13, 12)]:
        d.ellipse([int(w * sx) - sr, int(h * sy) - sr,
                   int(w * sx) + sr, int(h * sy) + sr],
                  fill=(120, 118, 110))
    return im


def art_bayesian(w, h):
    """Heeled sailing yacht in a night squall, wind streaks."""
    im = Image.new("RGB", (w, h), (24, 33, 52))
    d = ImageDraw.Draw(im)
    # wind streaks
    for i in range(7):
        y0 = 8 + i * 13
        d.line([(w * 0.55 + i * 6, y0), (w * 0.98, y0 - 16)],
               fill=(96, 116, 142), width=2)
    # sea
    d.rectangle([0, int(h * 0.62), w, h], fill=(38, 66, 80))
    for i in range(4):
        yy = int(h * 0.70) + i * 10
        d.arc([-12, yy - 5, w + 12, yy + 8], 200, 340, fill=(110, 150, 162))
    # heeled hull (drawn on its own layer, rotated)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    hx, hy = int(w * 0.42), int(h * 0.62)
    dl.polygon([(hx - 62, hy - 8), (hx + 62, hy - 8), (hx + 46, hy + 16),
                (hx - 46, hy + 16)], fill=(226, 220, 204))
    dl.line([(hx + 10, hy - 8), (hx + 10, hy - 84)], fill=(226, 220, 204),
            width=5)
    dl.polygon([(hx + 10, hy - 82), (hx + 10, hy - 10), (hx + 54, hy - 10)],
               fill=(214, 206, 188))
    dl.rectangle([hx - 20, hy - 30, hx - 12, hy - 8], fill=GOLD_LT)
    lay = lay.rotate(24, resample=Image.BICUBIC, center=(hx, hy))
    im.paste(lay, (0, 0), lay)
    return im


ARTISTS = {"jeffries": art_jeffries, "bridge": art_bridge,
           "bayesian": art_bayesian}


# ---- dotted world map ----
def _point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def load_land_polys():
    """Natural Earth 110m land, projected later; [] if unavailable."""
    try:
        with open(GEOJSON, encoding="utf-8") as fh:
            gj = json.load(fh)
    except Exception:
        return []
    polys = []
    for feat in gj.get("features", []):
        geom = feat.get("geometry") or {}
        typ, coords = geom.get("type"), geom.get("coordinates") or []
        if typ == "Polygon":
            polys.append(coords[0])
        elif typ == "MultiPolygon":
            for part in coords:
                polys.append(part[0])
    return polys


def draw_map(draw, box, stories):
    """Dotted land + numbered pins inside box=(x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=MAP_BG)
    f_title = F(DJB, 12)
    draw.text((x0 + 10, y0 + 8), "WHERE IT HAPPENED", font=f_title, fill=INK)
    draw.line([x0 + 10, y0 + 28, x1 - 10, y0 + 28], fill=LINE, width=1)

    mx0, my0, mx1, my1 = x0 + 8, y0 + 34, x1 - 8, y1 - 8
    lat_top, lat_bot = 80.0, -60.0

    def project(lon, lat):
        px = mx0 + (lon + 180.0) / 360.0 * (mx1 - mx0)
        py = my0 + (lat_top - lat) / (lat_top - lat_bot) * (my1 - my0)
        return px, py

    polys = load_land_polys()
    if polys:
        proj_polys = []
        for poly in polys:
            pp = [project(lon, lat) for lon, lat in poly]
            xs = [p[0] for p in pp]
            ys = [p[1] for p in pp]
            proj_polys.append((pp, min(xs), max(xs), min(ys), max(ys)))
        step = 5
        gx = mx0
        while gx <= mx1:
            gy = my0
            while gy <= my1:
                for pp, bx0, bx1, by0, by1 in proj_polys:
                    if bx0 - 2 <= gx <= bx1 + 2 and by0 - 2 <= gy <= by1 + 2:
                        if _point_in_poly(gx, gy, pp):
                            draw.ellipse([gx - 1.6, gy - 1.6, gx + 1.6,
                                          gy + 1.6], fill=DOT)
                            break
                gy += step
            gx += step
    else:
        # graticule-only fallback: no land data available
        for lon in range(-150, 181, 30):
            px, _ = project(lon, 0)
            draw.line([px, my0, px, my1], fill=LINE, width=1)
        for lat in range(-30, 81, 30):
            _, py = project(0, lat)
            draw.line([mx0, py, mx1, py], fill=LINE, width=1)

    # pins: true position + display offset (Europe is crowded)
    offsets = {1: (0, 0), 2: (-8, -8), 3: (10, -10), 4: (-12, 0),
               5: (0, 0), 6: (8, 4), 7: (0, 8)}
    for st in stories:
        lon, lat = st["pin"]
        tx, ty = project(lon, lat)
        dx, dy = offsets.get(st["n"], (0, 0))
        px, py = tx + dx, ty + dy
        if (dx, dy) != (0, 0):
            draw.line([tx, ty, px, py], fill=RUST, width=1)
            draw.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=RUST)
        number_badge(draw, int(px), int(py), st["n"], r=10)


# ---- cards ----
def card_art_image(st, tw, th):
    if st.get("image"):
        im = Image.open(os.path.join(ASSETS, st["image"])).convert("RGB")
        return cover_fit(im, tw, th)
    return cover_fit(ARTISTS[st["art"]](tw * 2, th * 2), tw, th)


def draw_lead_card(base, st, box):
    """Big card: image on top, headline + deck + source below."""
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=CARD,
                           outline=LINE, width=1)
    iw, ih = x1 - x0, 168
    art = card_art_image(st, iw, ih)
    mask = Image.new("L", (iw, ih), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, iw, ih], radius=6, fill=255)
    md.rectangle([0, ih - 8, iw, ih], fill=255)
    base.paste(art, (x0, y0), mask)
    number_badge(draw, x0 + 16, y0 + 16, st["n"])
    tx = x0 + 14
    ty = y0 + ih + 10
    tw = x1 - x0 - 28
    draw.text((tx, ty), st["head"], font=F(DJB, 18 if st["n"] == 1 else 16),
              fill=INK)
    ty += 26 if st["n"] == 1 else 24
    ty = draw_wrapped(draw, st["deck"], F(DJ, 12), INK, tx, ty, tw, 16,
                      max_lines=5)
    draw.text((tx, y1 - 20), st["src"], font=F(DJ, 9), fill=GREY)
    draw.text((x1 - 14 - draw.textlength(st["region"], font=F(DJB, 9)),
               y1 - 20), st["region"], font=F(DJB, 9), fill=TEAL)


def draw_medium_card(base, st, box):
    """Medium card: image on top, headline + deck + source below."""
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=CARD,
                           outline=LINE, width=1)
    iw, ih = x1 - x0, 108
    art = card_art_image(st, iw, ih)
    mask = Image.new("L", (iw, ih), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, iw, ih], radius=6, fill=255)
    md.rectangle([0, ih - 8, iw, ih], fill=255)
    base.paste(art, (x0, y0), mask)
    number_badge(draw, x0 + 14, y0 + 14, st["n"])
    tx = x0 + 12
    ty = y0 + ih + 8
    tw = x1 - x0 - 24
    ty = draw_wrapped(draw, st["head"], F(DJB, 14), INK, tx, ty, tw, 17,
                      max_lines=2)
    ty = draw_wrapped(draw, st["deck"], F(DJ, 11), INK, tx, ty + 2, tw, 14,
                      max_lines=4)
    draw.text((tx, y1 - 18), st["src"], font=F(DJ, 9), fill=GREY)
    draw.text((x1 - 12 - draw.textlength(st["region"], font=F(DJB, 9)),
               y1 - 18), st["region"], font=F(DJB, 9), fill=TEAL)


def draw_small_card(base, st, box):
    """Horizontal card: illustration thumb left, text right."""
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=CARD,
                           outline=LINE, width=1)
    tw_, th = 148, y1 - y0
    art = card_art_image(st, tw_, th)
    mask = Image.new("L", (tw_, th), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, tw_, th], radius=6, fill=255)
    md.rectangle([tw_ - 8, 0, tw_, th], fill=255)
    base.paste(art, (x0, y0), mask)
    number_badge(draw, x0 + 14, y0 + 14, st["n"])
    tx = x0 + tw_ + 10
    tw = x1 - tx - 10
    ty = draw_wrapped(draw, st["head"], F(DJB, 13), INK, tx, y0 + 9, tw, 16,
                      max_lines=2)
    ty = draw_wrapped(draw, st["deck"], F(DJ, 10), INK, tx, ty + 2, tw, 13,
                      max_lines=4)
    draw.text((tx, y1 - 17), st["src"], font=F(DJ, 9), fill=GREY)


# ---- page ----
def render():
    base = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(base)

    # header band
    draw.rectangle([0, 0, W, 88], fill=NAVY)
    draw.text((16, 12), "THE WORLD IN ONE PAGE", font=F(DJB, 30),
              fill=(255, 255, 255))
    f_date = F(DJB, 14)
    date_t = "THURSDAY 19 NOVEMBER 2026"
    draw.text((W - 16 - draw.textlength(date_t, font=f_date), 14), date_t,
              font=f_date, fill=GOLD_LT)
    regions = {}
    for st in STORIES:
        regions[st["region"]] = regions.get(st["region"], 0) + 1
    region_txt = " \u00b7 ".join(
        "%s %d" % (r, c) for r, c in sorted(regions.items()))
    sub = "7 STORIES \u00b7 %s \u00b7 ONE PAGE" % region_txt
    f_sub = F(DJ, 13)
    draw.text((W - 16 - draw.textlength(sub, font=f_sub), 40), sub,
              font=f_sub, fill=(205, 214, 228))
    draw.rectangle([0, 88, W, 91], fill=GOLD)

    # leads
    draw_lead_card(base, STORIES[0], (16, 100, 628, 390))
    draw_lead_card(base, STORIES[1], (636, 100, 1008, 390))

    # medium row
    draw_medium_card(base, STORIES[2], (16, 398, 344, 628))
    draw_medium_card(base, STORIES[3], (352, 398, 680, 628))
    draw_medium_card(base, STORIES[4], (688, 398, 1008, 628))

    # map + small cards
    draw_map(draw, (16, 636, 628, 876), STORIES)
    draw_small_card(base, STORIES[5], (636, 636, 1008, 752))
    draw_small_card(base, STORIES[6], (636, 760, 1008, 876))

    # numbers strip
    draw.rectangle([16, 884, 1008, 928], fill=SAND)
    draw.rectangle([16, 884, 1008, 928], outline=LINE, width=1)
    cell_w = (1008 - 16) / len(NUMBERS)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = 16 + cell_w * i
        if i:
            draw.line([cx, 890, cx, 922], fill=SAND_DK, width=1)
        draw.text((cx + 10, 890), num, font=F(DJB, 15), fill=NAVY)
        draw.text((cx + 10, 909), lab, font=F(DJ, 9), fill=GREY)

    # footer: DATE CHECK + sources
    fy = 938
    fy = draw_wrapped(draw, DATE_CHECK, F(DJ, 10), INK, 16, fy, 992, 14,
                      max_lines=2)
    draw.text((16, 972), SOURCES, font=F(DJ, 9), fill=GREY)
    return base


def main():
    img = render()
    img.save(os.path.join(HERE, "entry.png"), optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
