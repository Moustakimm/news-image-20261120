#!/usr/bin/env python3
"""Render 'The World Today - Friday 20 November 2026' as a dense 45-story
broadsheet, 1024x1024 PNG. Deterministic: no randomness, no network, no
timestamps. Uses only the Python standard library and Pillow."""

import hashlib
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
PAPER = (247, 243, 232)
PAPER2 = (238, 232, 214)
INK = (18, 24, 38)
NAVY = (14, 30, 62)
NAVY2 = (24, 48, 96)
RED = (178, 34, 34)
GOLD = (184, 134, 11)
TEAL = (0, 128, 128)
SKY = (70, 130, 180)
SLATE = (90, 100, 118)
WHITE = (255, 255, 255)
CREAM = (255, 248, 220)
PINK = (220, 120, 140)
GREEN = (34, 120, 60)
ORANGE = (220, 110, 30)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FONT_DIR + "DejaVuSerif-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANS_B = FONT_DIR + "DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap to a list of lines fitting max_w."""
    words = s.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, s, f, color, max_w, leading=None):
    if leading is None:
        leading = f.size + 3
    for line in wrap(draw, s, f, max_w):
        draw.text((x, y), line, font=f, fill=color)
        y += leading
    return y


def rrect(draw, box, fill=None, outline=None, width=1, radius=6):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline,
                           width=width)


# --- the day's stories ------------------------------------------------------
LEADS = [
    {
        "kicker": "WORLD COURT",
        "head": "Myanmar committed genocide against the Rohingya",
        "body": ("The International Court of Justice rules the 2017 crackdown was "
                 "state-sponsored genocide - the first such finding by the UN's top "
                 "court. Myanmar calls the ruling \"not fair\"."),
        "scene": "court",
        "badge": "9-6",
        "src": "ICJ - CNA",
    },
    {
        "kicker": "SUMMIT IN SHENZHEN",
        "head": "Trump, Xi and Putin hold first three-way summit",
        "body": ("After 90 minutes at Kylin Villa they sign a four-point joint "
                 "declaration: cutting nuclear risks, UN reform, stable energy "
                 "supply and the ICC's jurisdiction."),
        "scene": "summit",
        "badge": "3-WAY",
        "src": "Xinhua - AP",
    },
    {
        "kicker": "CYCLONE AKVAN",
        "head": "Akvan makes landfall in Odisha; no major damage",
        "body": ("The storm crosses the coast near Gopalpur on Friday morning, "
                 "winds 70-80 km/h gusting to 90; nearly 300,000 evacuated and "
                 "423 rescue teams are out."),
        "scene": "cyclone",
        "badge": "LANDFALL",
        "src": "IMD - The Hindu",
    },
]

MEDIUMS = [
    ("RIYADH", "Houthi missile damages Riyadh's tallest tower",
     "PIF Tower hit; windows blown out across eight floors.", "tower"),
    ("MARKETS", "Nikkei plunges 4.8% as global stocks slide",
     "Japan leads the sell-off; Taiwan -6.2%, Korea -5.2%.", "chart"),
    ("TECH", "Anthropic closes 17% above IPO price, then falls",
     "Day one ends near $97 on a record $81.3bn listing.", "rocket"),
    ("CLIMATE", "COP31 draft drops any call to phase out fossil fuels",
     "Negotiators strip the phase-out as talks reach the final day.", "leaf"),
    ("GAZA", "Israeli forces cross the Yellow Line in central Gaza",
     "Troops cross near Nuseirat - first incursion since the truce.", "border"),
    ("HORMUZ", "Iran war enters ninth month as tanker attacks grow",
     "A tanker catches fire after hitting a mine in the Strait.", "tanker"),
    ("SPACE", "Voyager 1 phones home from one light-day away",
     "26 billion km out - the first human object a light-day away.", "satellite"),
    ("HEALTH", "Kenya discharges its last Ebola patient",
     "The outbreak ends 37 days after the first case.", "cross"),
    ("GEORGIA", "Gas blast collapses a Tbilisi block; six dead",
     "A three-year-old girl is pulled alive from the rubble.", "blast"),
    ("WASHINGTON", "White House fires cyber chief after outages",
     "Sean Cairncross is out; Kirsten Davies named acting chief.", "shield"),
]

LIST_ITEMS = [
    "Danish MPs ratify US-Greenland security deal",
    "US and Venezuela sign military cooperation deal",
    "Hippo Fiona dies in Cincinnati days after swallowing a hat",
    "Scientists succeed in growing potatoes in moon soil",
    "Van Gogh sells for a record $190.4m after dispute",
    "Bukele registers for a third term in El Salvador",
    "Dozens missing after migrant boat capsizes off Senegal",
    "Drone strike kills 10 at a gold mine in Sudan",
    "IAEA: North Korea is expanding uranium enrichment",
    "Bangladesh deploys paramilitary amid unrest",
    "Trump bought up to $265,000 of Nvidia stock in Sept.",
    "Trump posthumously pardons MLB legend Pete Rose",
    "Musk feels \"pretty foolish\" over spending on Republicans",
    "Islam forecast to soon exceed Christianity as biggest faith",
    "Somalia orders the UAE ambassador to leave",
    "UK asks YouTube to remove a Russell Brand video",
    "Mexico's Sheinbaum hopes to seal a trade deal with Trump",
    "4 UK men guilty of sex crimes against a woman drugged by her husband",
    "US panel says India is targeting minorities",
    "US approves ~879,000 Nvidia/AMD AI chips for China",
    "Journalist barred from trilateral talks after Huang question",
    "Plant City shooting: man kills wife and 3 children",
    "US Army lead-azide detonation in Iowa postponed",
    "US Agriculture Dept hit by cyber incident",
    "China's used phones find new homes from Karachi to Algiers",
    "AI models favour US/UK accents, score others lowest",
    "Philippines and Chile sign a free trade agreement",
    "Singapore's Wong meets Xi in Shenzhen",
    "Myanmar calls the ICJ genocide ruling \"not fair\"",
    "Iraq orders an Iran-backed militia out of Jurf al-Nasr",
    "Russia strikes Kyiv overnight, damaging three bridges",
    "Japan's core inflation stays above target",
]

PINS = [
    ("The Hague", 4.3, 52.1), ("Shenzhen", 114.1, 22.5),
    ("Gopalpur", 84.9, 19.3), ("Riyadh", 46.7, 24.7),
    ("Tokyo", 139.7, 35.7), ("San Francisco", -122.4, 37.8),
    ("Antalya", 30.7, 36.9), ("Gaza", 34.5, 31.5),
    ("Hormuz", 56.5, 26.5), ("Pasadena", -118.1, 34.1),
    ("Nairobi", 36.8, -1.3), ("Tbilisi", 44.8, 41.7),
    ("Washington", -77.0, 38.9),
]

# Simplified continent outlines (lon, lat), equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-110, 71), (-95, 80), (-80, 73),
     (-65, 60), (-55, 47), (-65, 44), (-75, 35), (-81, 26), (-84, 30),
     (-90, 21), (-97, 16), (-104, 20), (-112, 26), (-120, 34), (-125, 42),
     (-124, 49), (-135, 58), (-150, 60), (-162, 58), (-168, 66)],
    # Greenland
    [(-55, 60), (-42, 60), (-30, 68), (-22, 74), (-30, 80), (-50, 79),
     (-58, 74), (-55, 60)],
    # South America
    [(-79, 9), (-72, 11), (-64, 10), (-58, 5), (-52, 4), (-50, 0),
     (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-55, -35),
     (-62, -41), (-66, -47), (-69, -52), (-71, -54), (-73, -44), (-73, -33),
     (-71, -20), (-75, -15), (-81, -6), (-81, 2), (-79, 9)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 30), (-5, 35), (10, 37), (20, 32),
     (30, 31), (35, 28), (39, 21), (43, 12), (51, 11), (48, 4), (41, -2),
     (40, -10), (36, -18), (33, -26), (27, -33), (19, -35), (15, -30),
     (12, -18), (13, -10), (9, 4), (0, 6), (-8, 5), (-13, 9), (-17, 15)],
    # Europe
    [(-10, 36), (-9, 43), (-4, 48), (-1, 49), (2, 51), (5, 53), (8, 57),
     (10, 59), (14, 56), (18, 56), (21, 58), (24, 62), (28, 66), (32, 70),
     (38, 68), (42, 66), (40, 60), (38, 56), (33, 52), (30, 48), (26, 45),
     (23, 40), (19, 42), (15, 44), (12, 44), (8, 44), (3, 42), (0, 38),
     (-2, 37), (-6, 36), (-10, 36)],
    # Asia
    [(30, 70), (40, 68), (50, 69), (60, 70), (68, 73), (78, 73), (88, 75),
     (98, 76), (108, 74), (118, 73), (128, 72), (138, 72), (148, 71),
     (158, 69), (168, 66), (178, 65), (170, 62), (162, 60), (158, 53),
     (150, 46), (142, 40), (135, 35), (130, 33), (127, 36), (122, 39),
     (120, 31), (116, 23), (110, 20), (106, 10), (101, 8), (97, 15),
     (92, 21), (88, 22), (83, 18), (80, 14), (77, 8), (74, 15), (72, 20),
     (69, 23), (66, 25), (62, 25), (58, 26), (55, 26), (51, 28), (49, 30),
     (46, 29), (43, 20), (40, 15), (39, 21), (38, 26), (36, 29), (34, 31),
     (32, 36), (30, 36), (28, 41), (30, 46), (32, 52), (30, 58), (28, 63),
     (30, 70)],
    # Australia
    [(113, -22), (114, -30), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (136, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -23), (146, -19), (142, -15), (142, -11), (137, -12),
     (135, -15), (132, -12), (129, -14), (126, -14), (122, -17), (118, -20),
     (113, -22)],
]


# --- scene drawing -----------------------------------------------------------
def scene_court(draw, x, y, w, h):
    """A courthouse: pediment, columns, steps, scales of justice."""
    draw.rectangle([x, y, x + w, y + h], fill=(30, 48, 90))
    # sky glow
    draw.ellipse([x + w - 70, y + 8, x + w - 20, y + 58], fill=(255, 214, 120))
    # pediment
    cx = x + w // 2
    draw.polygon([(cx - 90, y + 62), (cx + 90, y + 62), (cx, y + 28)],
                 fill=(232, 226, 205))
    draw.ellipse([cx - 12, y + 40, cx + 12, y + 64], fill=GOLD)
    # columns
    for i in range(5):
        col_x = cx - 80 + i * 40
        draw.rectangle([col_x, y + 66, col_x + 14, y + h - 22],
                       fill=(245, 240, 224))
        draw.rectangle([col_x - 3, y + 62, col_x + 17, y + 68],
                       fill=(220, 214, 192))
    # steps
    draw.rectangle([x + 20, y + h - 22, x + w - 20, y + h - 16],
                   fill=(200, 194, 172))
    draw.rectangle([x + 10, y + h - 15, x + w - 10, y + h - 9],
                   fill=(180, 174, 152))
    # scales of justice, small, bottom right
    sx, sy = x + w - 52, y + h - 52
    draw.line([sx + 14, sy, sx + 14, sy + 26], fill=GOLD, width=3)
    draw.line([sx, sy + 6, sx + 28, sy + 6], fill=GOLD, width=3)
    draw.arc([sx - 2, sy + 8, sx + 10, sy + 22], 0, 180, fill=GOLD, width=2)
    draw.arc([sx + 18, sy + 8, sx + 30, sy + 22], 0, 180, fill=GOLD, width=2)
    draw.ellipse([sx + 8, sy - 6, sx + 20, sy + 6], fill=GOLD)


def scene_summit(draw, x, y, w, h):
    """Three leaders at a summit table with three flags behind them."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 52, 96))
    # flags: US, China, Russia
    flags = [
        ((200, 40, 40), (255, 255, 255), (30, 60, 140)),   # US
        ((200, 30, 30), (255, 220, 60), (200, 30, 30)),     # China
        ((255, 255, 255), (30, 90, 180), (200, 40, 40)),    # Russia
    ]
    for i, (c1, c2, c3) in enumerate(flags):
        fx = x + 18 + i * (w - 36) // 3
        fw = (w - 36) // 3 - 8
        draw.rectangle([fx, y + 10, fx + fw, y + 26], fill=c1)
        draw.rectangle([fx, y + 26, fx + fw, y + 42], fill=c2)
        draw.rectangle([fx, y + 42, fx + fw, y + 58], fill=c3)
        if i == 0:  # stars canton
            draw.rectangle([fx, y + 10, fx + fw // 2, y + 26],
                           fill=(30, 40, 90))
            for sy in (y + 14, y + 20):
                for sx in (fx + 5, fx + 14, fx + 23):
                    draw.ellipse([sx, sy, sx + 3, sy + 3], fill=WHITE)
        if i == 1:  # yellow stars
            for sx, sy in ((fx + 8, y + 14), (fx + 20, y + 18),
                           (fx + 26, y + 28), (fx + 12, y + 32)):
                draw.ellipse([sx, sy, sx + 4, sy + 4], fill=(255, 220, 60))
    # table
    draw.rectangle([x + 8, y + h - 46, x + w - 8, y + h - 30],
                   fill=(120, 72, 32))
    draw.rectangle([x + 8, y + h - 30, x + w - 8, y + h - 26],
                   fill=(90, 52, 22))
    # three figures: suits with faces
    suits = [(30, 60, 120), (120, 30, 30), (40, 80, 50)]
    skins = [(232, 196, 160), (240, 205, 170), (225, 190, 155)]
    for i in range(3):
        fx = x + 30 + i * (w - 60) // 2
        fy = y + h - 108
        draw.ellipse([fx, fy, fx + 34, fy + 34], fill=skins[i])
        draw.rectangle([fx - 8, fy + 34, fx + 42, y + h - 46],
                       fill=suits[i])
        draw.polygon([(fx + 12, fy + 34), (fx + 22, fy + 34),
                      (fx + 17, fy + 52)], fill=WHITE)
        # hair
        draw.arc([fx, fy - 2, fx + 34, fy + 14], 180, 360,
                 fill=(60, 50, 40), width=6)
    # nameplates
    for i, name in enumerate(("TRUMP", "XI", "PUTIN")):
        fx = x + 30 + i * (w - 60) // 2
        f = font(SANS_B, 11)
        tw = text_w(draw, name, f)
        draw.rectangle([fx + 17 - tw // 2 - 4, y + h - 44,
                        fx + 17 + tw // 2 + 4, y + h - 30],
                       fill=WHITE)
        draw.text((fx + 17 - tw // 2, y + h - 43), name, font=f, fill=INK)


def scene_cyclone(draw, x, y, w, h):
    """A cyclone spiral over a coastline, with rain bands."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 60, 110))
    # sea
    draw.rectangle([x, y + h - 46, x + w, y + h], fill=(20, 90, 140))
    # coastline
    draw.polygon([(x, y + h - 46), (x + w // 3, y + h - 60),
                  (x + 2 * w // 3, y + h - 40), (x + w, y + h - 52),
                  (x + w, y + h), (x, y + h)], fill=(70, 130, 80))
    # spiral arms
    cx, cy = x + w // 2, y + 62
    for r, col in ((66, (220, 235, 245)), (50, (180, 210, 235)),
                   (36, (140, 185, 225)), (22, (100, 160, 210))):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 60, fill=col, width=7)
        draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 240, fill=col, width=7)
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=WHITE)
    # rain streaks
    for i in range(14):
        rx = x + 10 + (i * 23) % (w - 20)
        ry = y + 12 + (i * 7) % 40
        draw.line([rx, ry, rx - 4, ry + 12], fill=(200, 220, 240), width=2)
    # houses on the coast
    for i, hx in enumerate((x + 14, x + w - 46)):
        draw.rectangle([hx, y + h - 34, hx + 30, y + h - 18],
                       fill=(240, 220, 180))
        draw.polygon([(hx - 3, y + h - 34), (hx + 15, y + h - 46),
                      (hx + 33, y + h - 34)], fill=(160, 60, 50))


def scene_icon(draw, x, y, w, h, kind):
    """Small recognisable scene for a medium story."""
    if kind == "tower":
        draw.rectangle([x, y, x + w, y + h], fill=(40, 60, 100))
        draw.rectangle([x + w // 2 - 16, y + 6, x + w // 2 + 16, y + h - 8],
                       fill=(200, 210, 225))
        draw.rectangle([x + w // 2 - 22, y + 2, x + w // 2 + 22, y + 8],
                       fill=(160, 170, 190))
        for fy in range(y + 12, y + h - 12, 8):
            draw.rectangle([x + w // 2 - 12, fy, x + w // 2 + 12, fy + 3],
                           fill=(250, 200, 80))
        draw.polygon([(x + w // 2 - 26, y + h - 8), (x + w // 2 + 26, y + h - 8),
                      (x + w // 2, y + h - 30)], fill=(255, 120, 40))
        draw.ellipse([x + w - 30, y + 4, x + w - 10, y + 24],
                     fill=(255, 220, 120))
    elif kind == "chart":
        draw.rectangle([x, y, x + w, y + h], fill=(30, 50, 40))
        draw.line([x + 6, y + h - 8, x + w - 6, y + 8], fill=RED, width=4)
        for i, px in enumerate((x + 12, x + 40, x + 68, x + 96, x + 124)):
            py = y + h - 14 - i * 10
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=WHITE)
        draw.text((x + 8, y + 6), "-4.8%", font=font(SANS_B, 16), fill=RED)
    elif kind == "rocket":
        draw.rectangle([x, y, x + w, y + h], fill=(20, 40, 80))
        draw.polygon([(x + w // 2, y + 6), (x + w // 2 - 12, y + 30),
                      (x + w // 2 + 12, y + 30)], fill=(220, 60, 60))
        draw.rectangle([x + w // 2 - 12, y + 30, x + w // 2 + 12, y + h - 16],
                       fill=(230, 230, 235))
        draw.ellipse([x + w // 2 - 5, y + 36, x + w // 2 + 5, y + 46],
                     fill=SKY)
        draw.polygon([(x + w // 2 - 12, y + h - 16), (x + w // 2 - 22, y + h - 4),
                      (x + w // 2 - 12, y + h - 8)], fill=(220, 60, 60))
        draw.polygon([(x + w // 2 + 12, y + h - 16), (x + w // 2 + 22, y + h - 4),
                      (x + w // 2 + 12, y + h - 8)], fill=(220, 60, 60))
        draw.polygon([(x + w // 2 - 5, y + h - 16), (x + w // 2 + 5, y + h - 16),
                      (x + w // 2, y + h - 2)], fill=(255, 180, 40))
    elif kind == "leaf":
        draw.rectangle([x, y, x + w, y + h], fill=(20, 70, 50))
        draw.ellipse([x + 20, y + 8, x + w - 20, y + h - 8], fill=(60, 160, 90))
        draw.line([x + w // 2, y + 10, x + w // 2, y + h - 10],
                  fill=(20, 90, 50), width=3)
        for i in range(4):
            ly = y + 16 + i * 10
            draw.line([x + w // 2, ly, x + w // 2 - 22, ly + 8],
                      fill=(20, 90, 50), width=2)
            draw.line([x + w // 2, ly, x + w // 2 + 22, ly + 8],
                      fill=(20, 90, 50), width=2)
        draw.line([x + 10, y + h - 12, x + w - 10, y + h - 12],
                  fill=RED, width=4)
    elif kind == "border":
        draw.rectangle([x, y, x + w, y + h], fill=(90, 80, 60))
        draw.rectangle([x, y, x + w // 2, y + h], fill=(200, 180, 120))
        draw.line([x + w // 2, y, x + w // 2, y + h], fill=RED, width=4)
        for i in range(4):
            draw.line([x + w // 2 - 8, y + 10 + i * 12,
                       x + w // 2 + 8, y + 16 + i * 12], fill=RED, width=3)
        draw.rectangle([x + 8, y + h - 26, x + 34, y + h - 8],
                       fill=(40, 60, 40))
        draw.rectangle([x + w - 34, y + h - 26, x + w - 8, y + h - 8],
                       fill=(40, 60, 40))
    elif kind == "tanker":
        draw.rectangle([x, y, x + w, y + h], fill=(20, 60, 100))
        draw.rectangle([x, y + h - 22, x + w, y + h], fill=(16, 90, 140))
        draw.polygon([(x + 14, y + h - 26), (x + w - 14, y + h - 26),
                      (x + w - 30, y + h - 12), (x + 30, y + h - 12)],
                     fill=(180, 60, 40))
        draw.rectangle([x + w // 2 - 8, y + h - 44, x + w // 2 + 14, y + h - 26],
                       fill=(240, 235, 220))
        draw.line([x + w // 2 + 2, y + h - 56, x + w // 2 + 2, y + h - 44],
                  fill=WHITE, width=2)
        draw.polygon([(x + w // 2 - 34, y + 8), (x + w // 2 - 20, y + 26),
                      (x + w // 2 - 44, y + 26)], fill=(255, 140, 40))
        draw.ellipse([x + w // 2 + 26, y + 10, x + w // 2 + 42, y + 26],
                     fill=(255, 180, 60))
    elif kind == "satellite":
        draw.rectangle([x, y, x + w, y + h], fill=(10, 16, 40))
        for i in range(30):
            sx = x + (i * 37) % w
            sy = y + (i * 23) % h
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=WHITE)
        # dish
        draw.arc([x + w // 2 - 26, y + 12, x + w // 2 + 26, y + 52], 0, 180,
                 fill=(200, 210, 230), width=5)
        draw.line([x + w // 2, y + 32, x + w // 2, y + h - 14],
                  fill=(200, 210, 230), width=4)
        draw.line([x + w // 2 - 12, y + h - 14, x + w // 2 + 12, y + h - 14],
                  fill=(200, 210, 230), width=4)
        # signal waves
        for r in (18, 28):
            draw.arc([x + w // 2 - r, y + 34 - r, x + w // 2 + r, y + 34 + r],
                     270, 360, fill=(120, 200, 255), width=3)
            draw.arc([x + w // 2 - r, y + 34 - r, x + w // 2 + r, y + 34 + r],
                     180, 270, fill=(120, 200, 255), width=3)
    elif kind == "cross":
        draw.rectangle([x, y, x + w, y + h], fill=(220, 235, 220))
        draw.ellipse([x + w // 2 - 26, y + 8, x + w // 2 + 26, y + 60],
                     fill=WHITE, outline=GREEN, width=3)
        draw.rectangle([x + w // 2 - 6, y + 16, x + w // 2 + 6, y + 52],
                       fill=GREEN)
        draw.rectangle([x + w // 2 - 18, y + 28, x + w // 2 + 18, y + 40],
                       fill=GREEN)
    elif kind == "blast":
        draw.rectangle([x, y, x + w, y + h], fill=(50, 40, 40))
        cx, cy = x + w // 2, y + h // 2
        for r, col in ((34, (255, 140, 40)), (24, (255, 200, 60)),
                       (14, (255, 240, 160))):
            pts = []
            for k in range(12):
                ang = k * 30
                import math
                rr = r if k % 2 == 0 else r // 2
                pts.append((cx + rr * math.cos(math.radians(ang)),
                            cy + rr * math.sin(math.radians(ang))))
            draw.polygon(pts, fill=col)
        draw.rectangle([x + 8, y + h - 16, x + w - 8, y + h - 8],
                       fill=(120, 110, 100))
    elif kind == "shield":
        draw.rectangle([x, y, x + w, y + h], fill=(30, 40, 70))
        cx, cy = x + w // 2, y + h // 2 - 4
        draw.polygon([(cx - 24, cy - 22), (cx + 24, cy - 22), (cx + 24, cy + 4),
                      (cx, cy + 28), (cx - 24, cy + 4)], fill=(70, 130, 200))
        draw.polygon([(cx - 18, cy - 16), (cx + 18, cy - 16), (cx + 18, cy + 2),
                      (cx, cy + 20), (cx - 18, cy + 2)], fill=(30, 60, 120))
        draw.line([cx - 8, cy + 2, cx - 2, cy + 10, cx + 10, cy - 8],
                  fill=(120, 255, 140), width=4)


# --- layout ------------------------------------------------------------------
def draw_masthead(draw):
    draw.rectangle([6, 6, 1018, 72], fill=NAVY)
    draw.rectangle([6, 6, 1018, 72], outline=GOLD, width=2)
    f_title = font(SERIF_B, 40)
    title = "THE WORLD TODAY"
    tw = text_w(draw, title, f_title)
    draw.text(((W - tw) / 2, 12), title, font=f_title, fill=WHITE)
    f_date = font(SANS_B, 19)
    date = "Friday 20 November 2026"
    tw = text_w(draw, date, f_date)
    draw.text(((W - tw) / 2, 76), date, font=f_date, fill=NAVY)
    f_kick = font(SANS_B, 13)
    draw.text((14, 78), "45 STORIES", font=f_kick, fill=RED)
    right = "6 CONTINENTS"
    tw = text_w(draw, right, f_kick)
    draw.text((1010 - tw, 78), right, font=f_kick, fill=RED)
    # UTC timeline strip
    y = 102
    draw.rectangle([14, y, 1010, y + 2], fill=SLATE)
    f_hr = font(SANS, 9)
    for hr in range(0, 24, 3):
        x = 14 + hr * (996 / 23)
        draw.line([x, y - 3, x, y + 7], fill=SLATE, width=2)
        lab = "%02d:00 UTC" % hr
        draw.text((x - 14, y + 8), lab, font=f_hr, fill=SLATE)
    draw.ellipse([14 + 2 * (996 / 23) - 4, y - 4, 14 + 2 * (996 / 23) + 4,
                  y + 4], fill=RED)


def draw_lead(draw, lead, x, y, w):
    h = 296
    rrect(draw, [x, y, x + w, y + h], fill=WHITE, outline=NAVY, width=2,
          radius=4)
    # scene
    sx, sy, sw, sh = x + 6, y + 6, w - 12, 148
    if lead["scene"] == "court":
        scene_court(draw, sx, sy, sw, sh)
    elif lead["scene"] == "summit":
        scene_summit(draw, sx, sy, sw, sh)
    else:
        scene_cyclone(draw, sx, sy, sw, sh)
    # badge stamp
    f_badge = font(SANS_B, 12)
    bw = text_w(draw, lead["badge"], f_badge) + 12
    bx = x + w - bw - 12
    by = sy + 8
    draw.polygon([(bx, by), (bx + bw, by), (bx + bw - 6, by + 20),
                  (bx + 6, by + 20)], fill=RED)
    draw.text((bx + 6, by + 3), lead["badge"], font=f_badge, fill=WHITE)
    # kicker
    f_kick = font(SANS_B, 11)
    draw.text((x + 10, y + 162), lead["kicker"], font=f_kick, fill=RED)
    # headline
    f_head = font(SANS_B, 17)
    ty = draw_wrapped(draw, x + 10, y + 180, lead["head"], f_head, INK,
                      w - 20, leading=21)
    # body
    f_body = font(SANS, 12)
    draw_wrapped(draw, x + 10, ty + 4, lead["body"], f_body, INK, w - 20,
                 leading=15)
    # source
    f_src = font(SANS, 10)
    draw.text((x + 10, y + h - 18), lead["src"], font=f_src, fill=SLATE)


def draw_medium(draw, item, x, y, w, h):
    kicker, head, body, kind = item
    rrect(draw, [x, y, x + w, y + h], fill=WHITE, outline=SLATE, width=1,
          radius=4)
    scene_icon(draw, x + 4, y + 4, w - 8, 58, kind)
    f_kick = font(SANS_B, 10)
    draw.text((x + 6, y + 66), kicker, font=f_kick, fill=RED)
    f_head = font(SANS_B, 12)
    ty = draw_wrapped(draw, x + 6, y + 80, head, f_head, INK, w - 12,
                      leading=14)
    f_body = font(SANS, 10)
    draw_wrapped(draw, x + 6, ty + 2, body, f_body, SLATE, w - 12, leading=12)


def draw_map(draw, x, y, w, h):
    rrect(draw, [x, y, x + w, y + h], fill=(225, 235, 245),
          outline=NAVY, width=2, radius=4)
    f_t = font(SANS_B, 13)
    draw.text((x + 10, y + 8), "THE WORLD IN ONE DAY", font=f_t, fill=NAVY)
    # map area
    mx, my, mw, mh = x + 8, y + 30, w - 16, h - 62
    draw.rectangle([mx, my, mx + mw, my + mh], fill=(200, 222, 240))
    # continents (lon -180..180, lat -60..85)
    def proj(lon, lat):
        px = mx + (lon + 180) / 360.0 * mw
        py = my + (85 - lat) / 145.0 * mh
        return (px, py)
    for poly in CONTINENTS:
        draw.polygon([proj(lon, lat) for lon, lat in poly],
                     fill=(110, 160, 100), outline=(70, 120, 70))
    # pins
    for name, lon, lat in PINS:
        px, py = proj(lon, lat)
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED,
                     outline=WHITE, width=1)
    # legend
    f_l = font(SANS, 10)
    draw.text((x + 10, y + h - 26), "13 pins: the day's stories, placed",
              font=f_l, fill=SLATE)


def draw_datecheck(draw, x, y, w, h):
    rrect(draw, [x, y, x + w, y + h], fill=CREAM, outline=GOLD, width=2,
          radius=4)
    f_t = font(SANS_B, 13)
    draw.text((x + 10, y + 8), "DATE CHECK", font=f_t, fill=NAVY)
    f_b = font(SANS, 12)
    lines = [
        "Left out on purpose - not 20 Nov:",
        "  - US strike on Qeshm Island (17 Nov)",
        "  - Crimea bridge's second strike (17 Nov)",
        "Not yet:",
        "  - COP31 final deal, due to close Friday",
        "  - Akvan's remnants reaching inland, due Sat.",
    ]
    ty = y + 30
    for line in lines:
        draw.text((x + 10, ty), line, font=f_b,
                  fill=RED if line.startswith("Left") or line.startswith("Not")
                  else INK)
        ty += 17


def draw_list(draw, x, y, w, h):
    f_t = font(SANS_B, 14)
    draw.text((x, y), "ALSO ON FRIDAY 20 NOVEMBER", font=f_t, fill=NAVY)
    draw.line([x, y + 22, x + w, y + 22], fill=NAVY, width=2)
    f_n = font(SANS_B, 11)
    f_b = font(SANS, 11)
    col_w = (w - 16) // 2
    row_h = (h - 30) // 16
    for i, item in enumerate(LIST_ITEMS):
        col = 0 if i < 16 else 1
        row = i % 16
        ix = x + col * (col_w + 16)
        iy = y + 28 + row * row_h
        draw.text((ix, iy), "%d." % (i + 14), font=f_n, fill=RED)
        # shorten to fit one line
        text = item
        while text_w(draw, text, f_b) > col_w - 28 and len(text) > 20:
            text = text[:len(text) - 4].rstrip() + "..."
        draw.text((ix + 26, iy), text, font=f_b, fill=INK)


# --- compose -----------------------------------------------------------------
def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    # outer border
    draw.rectangle([2, 2, W - 3, H - 3], outline=NAVY, width=3)
    draw_masthead(draw)
    # leads: three columns
    lead_y = 124
    lead_w = 330
    lead_xs = [8, 347, 686]
    for lead, lx in zip(LEADS, lead_xs):
        draw_lead(draw, lead, lx, lead_y, lead_w)
    # mediums: five columns x two rows
    med_y0 = 428
    med_w = 200
    med_h = 106
    med_xs = [8, 210, 412, 614, 816]
    for i, item in enumerate(MEDIUMS):
        col = i % 5
        row = i // 5
        draw_medium(draw, item, med_xs[col], med_y0 + row * (med_h + 4),
                    med_w, med_h)
    # bottom band
    band_y = 652
    draw_map(draw, 8, band_y, 372, 232)
    draw_datecheck(draw, 8, band_y + 238, 372, 132)
    draw_list(draw, 392, band_y, 624, 372)
    # sources line
    f_src = font(SANS, 10)
    src = ("Sources: ICJ - CNA - Xinhua - AP - IMD - The Hindu - NDTV - SCMP - "
           "Reuters - CNBC TV18 - Dawn - NASA - AFP - Times Now - Times of India")
    draw.text((14, 1002), src, font=f_src, fill=SLATE)
    return img


def main():
    img = render()
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img.save(out, format="PNG")
    with open(out, "rb") as fh:
        data = fh.read()
    print("wrote %s (%d bytes) sha256=%s" %
          (out, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
