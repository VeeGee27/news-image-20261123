#!/usr/bin/env python3
"""Render the NEWS-23 front page: 39 stories from Monday 23 November 2026.

Dense serif newspaper front page, warm newsprint, numbered world map on true
lat/lon coordinates, DATE CHECK box, verification tags. Deterministic output.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (244, 238, 222)
PAPER2 = (238, 230, 208)
INK = (26, 24, 20)
INK_SOFT = (60, 56, 48)
MUTED = (110, 102, 86)
RULE = (150, 138, 112)
ACCENT = (158, 28, 28)          # deep newspaper red
ACCENT_DK = (120, 18, 18)
GOLD = (176, 132, 40)
BLUE = (31, 58, 95)
BLUE_LT = (226, 232, 240)
SEA = (202, 214, 212)
LAND = (231, 222, 198)
LAND_EDGE = (168, 152, 120)
GREEN = (38, 92, 50)
GREEN_BG = (226, 236, 224)

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu"
F_SERIF = os.path.join(FD, "DejaVuSerif.ttf")
F_SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
F_SANS = os.path.join(FD, "DejaVuSans.ttf")
F_SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")
F_MONO = os.path.join(FD, "DejaVuSansMono.ttf")
F_MONO_B = os.path.join(FD, "DejaVuSansMono-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- helpers
def wrap(draw, text, fnt, width):
    """Greedy word wrap. Returns list of lines that fit `width` px."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def rule(draw, x0, x1, y, fill=RULE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def double_rule(draw, x0, x1, y, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=2)
    draw.line([(x0, y + 3), (x1, y + 3)], fill=fill, width=1)


def box(draw, x0, y0, x1, y1, fill=None, outline=None, width=1):
    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)


def make_paper():
    """Warm newsprint base with deterministic fibre speckle + faint columns."""
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(20261123)
    for _ in range(2600):
        x = rng.randrange(W)
        y = rng.randrange(H)
        a = rng.randrange(5, 15)
        c = rng.choice([(120, 100, 60), (255, 252, 240), (180, 160, 110)])
        d.point((x, y), fill=c + (a,))
    # faint vertical press lines
    for x in (12, 1011):
        d.line([(x, 10), (x, H - 10)], fill=(170, 152, 110, 60), width=1)
    # faint horizontal crease bands
    for y in (252, 620):
        d.rectangle([8, y, W - 9, y + 1], fill=(190, 172, 128, 28))
    return img


def tag(draw, x, y, text, fill=ACCENT, fg=(250, 246, 236)):
    """Small verification tag, e.g. CONFIRMED — REUTERS."""
    f = font(F_SANS_B, 11)
    w = draw.textlength(text, font=f) + 10
    h = 16
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    draw.text((x + 5, y + 2), text, font=f, fill=fg)
    return w


# ---------------------------------------------------------------- land polygons
# Hand-drawn, simplified continent outlines (lon, lat). Deterministic, no data
# files: these are my own coarse shapes, adequate at map scale.
CONTINENTS = [
    # North America (incl. Greenland + Central America taper)
    [(-168, 66), (-158, 71), (-140, 70), (-125, 72), (-110, 68), (-95, 69),
     (-85, 66), (-80, 62), (-76, 58), (-68, 58), (-65, 50), (-60, 47),
     (-70, 44), (-75, 39), (-80, 32), (-81, 26), (-84, 30), (-89, 30),
     (-91, 19), (-92, 15), (-83, 9), (-79, 9), (-86, 13), (-90, 14),
     (-92, 15), (-97, 16), (-105, 20), (-110, 23), (-114, 28), (-117, 33),
     (-122, 37), (-124, 40), (-124, 42), (-124, 48), (-132, 56), (-145, 60), (-155, 58), (-165, 60),
     (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
     (-20, 74), (-25, 78), (-32, 80), (-45, 81), (-58, 80), (-62, 76),
     (-68, 76), (-66, 70), (-58, 64)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-71, -18),
     (-70, -23), (-70, -33), (-72, -41), (-74, -50), (-70, -55), (-66, -55),
     (-65, -45), (-62, -39), (-58, -34), (-48, -28), (-41, -23), (-39, -17),
     (-35, -9), (-35, -6), (-43, -3), (-50, 0), (-52, 4), (-60, 8),
     (-62, 11), (-72, 12), (-79, 9)],
    # Africa
    [(-17, 15), (-17, 21), (-13, 27), (-9, 31), (-5, 35), (10, 37),
     (11, 34), (20, 32.6), (30, 31), (33, 27), (37, 22), (39, 21),
     (43, 12), (51, 11), (51, 2), (46, -1), (41, -4), (40, -10),
     (36, -18), (33, -26), (27, -33), (19, -35), (15, -27), (12, -18),
     (13, -13), (9, -2), (9, 4), (-8, 5), (-13, 8), (-17, 15)],
    # Eurasia (Europe + Asia, one mass)
    [(-10, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 49),
     (1, 51), (5, 53), (8, 57), (10, 59), (18, 56), (21, 55),
     (24, 58), (28, 59), (30, 60), (30, 62), (32, 70), (45, 68),
     (55, 68), (66, 69), (75, 72), (85, 73), (100, 76), (110, 74),
     (120, 73), (130, 72), (140, 72), (150, 70), (160, 70), (170, 67),
     (178, 66), (170, 60), (162, 56), (158, 52), (162, 60), (170, 60),
     (162, 60), (158, 52), (156, 51), (150, 59), (142, 59), (141, 52),
     (140, 45), (142, 40), (135, 35), (130, 33), (127, 35), (127, 40),
     (130, 42), (135, 43), (139, 39), (141, 45), (142, 50), (140, 53),
     (137, 54), (135, 44), (130, 42), (128.5, 39.5), (129.5, 36),
     (127.5, 35), (126.3, 35.5), (126.8, 38), (124.8, 39.8), (122, 39),
     (120, 35), (122, 31), (120, 28), (110, 20), (108, 18), (105, 9),
     (103.5, 5), (101.5, 2), (100, 1.5), (99.5, 4), (98.5, 7), (98, 10),
     (97, 15), (94, 17), (92, 21),
     (89, 22), (87, 21), (85, 19), (80, 13), (77, 8), (75, 12),
     (73, 16), (72, 20), (68, 22), (66, 25), (61, 25), (57, 26),
     (54, 26), (52, 27), (50, 29), (48, 30), (51, 24), (54, 24),
     (57, 22), (59, 22), (58, 24), (57, 26), (54, 26), (52, 25),
     (50, 26), (48, 27), (44, 29), (39, 21), (43, 12), (43, 11),
     (39, 15), (39, 20), (38, 22), (35, 28), (34, 31), (36, 36),
     (30, 36), (27, 37), (26, 39), (23, 36), (22, 37), (19, 42),
     (12, 44), (8, 44), (3, 43), (-1, 44), (-2, 48), (-4, 48),
     (-9, 43), (-10, 37)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
     (1, 51), (-2, 50), (-5, 50)],
    # Ireland
    [(-10, 52), (-8, 51), (-6, 52), (-6, 55), (-8, 55), (-10, 54),
     (-10, 52)],
    # Japan (Honshu chain, simplified)
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
     (140, 38), (141, 41), (143, 42), (145, 44), (142, 44), (141, 42),
     (140, 40), (139, 38), (137, 37), (135, 34), (133, 34), (131, 33),
     (130, 31)],
    # Borneo
    [(109, 1), (111, 2), (113, 4), (117, 6), (119, 6), (118, 2),
     (117, -2), (115, -3), (112, -3), (110, -2), (109, 1)],
    # Sumatra
    [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (104, -5),
     (100, -2), (97, 2), (95, 5)],
    # Java
    [(105, -6), (108, -7), (111, -7), (114, -8), (114, -8), (110, -8),
     (106, -7), (105, -6)],
    # New Guinea
    [(131, -1), (135, -2), (138, -3), (141, -3), (144, -4), (147, -6),
     (150, -9), (146, -8), (142, -8), (138, -8), (135, -5), (132, -3),
     (131, -1)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
     (129, -32), (132, -32), (136, -35), (140, -38), (145, -38),
     (150, -37), (153, -27), (153, -24), (150, -22), (146, -19),
     (142, -11), (142, -15), (136, -15), (135, -12), (132, -12),
     (130, -13), (126, -14), (122, -17), (117, -20), (113, -22)],
    # New Zealand (two islands, simplified)
    [(167, -45), (168, -44), (170, -42), (173, -41), (177, -38),
     (178, -39), (176, -41.3), (174, -41.5), (172, -43), (169, -46),
     (167, -45)],
    # Iceland
    [(-22, 64), (-18, 63), (-14, 64), (-15, 66), (-19, 66), (-22, 65),
     (-22, 64)],
    # Taiwan
    [(120, 22), (121, 23), (121.9, 25), (121.3, 25.3), (120, 25), (120, 22)],
    # Luzon, Philippines (for Mayon)
    [(120, 18.5), (122, 18), (124.5, 14), (123.5, 13), (122, 13.5),
     (121, 14.5), (120, 16), (120, 18.5)],
    # Sri Lanka
    [(80, 6), (81, 7), (81, 9), (80, 9), (80, 6)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -25), (45, -25),
     (44, -20), (44, -16)],
]

# ---------------------------------------------------------------- story data
# (num, headline, deck, tag, lat, lon, art)
# tag: ("CONFIRMED", source) or ("REPORTED", source). All dated Mon 23 Nov 2026.
HEROES = [
    (1, "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
     "Seven sea drones sank the Merkury at Benghazi; a Ka-27 aboard was "
     "destroyed.",
     "CONFIRMED — AP", 32.12, 20.07, "ship"),
    (2, "TAIWAN REBOUNDS AS SHORT-SELLING BAN TAKES HOLD",
     "The ban took effect as Taipei's market swung 1,213 points and closed "
     "up 2.16% at 36,811.89.",
     "CONFIRMED — REUTERS", 25.03, 121.57, "chart"),
    (3, "NATO MEETS AS POLAND CONFIRMS RUSSIAN MISSILES",
     "All three cruise missiles that fell on Friday were Russian Kh-101s, "
     "prosecutors said Sunday.",
     "CONFIRMED — NATO / AP", 50.85, 4.35, "star"),
]

# (num, headline, deck, tag, lat, lon, art, region)
MIDS = [
    (4, "INDIA'S RECORD 720 DENIED AS TEST ENDS IN DRAW",
     "Mitchell (49*) kept New Zealand's second innings alive at Wellington "
     "as India declared on a record 720 for 9; Rahul hit 136 and Pant 128 "
     "in the drawn first Test.",
     "CONFIRMED — IANS", -41.29, 174.78, "cricket", "Oceania"),
    (5, "M6.5 QUAKE STRIKES OFF VANUATU",
     "A magnitude 6.5 quake struck at 02:40 UTC, 601 km deep beneath the "
     "Pacific; no tsunami threat was issued for the island nation.",
     "CONFIRMED — USGS", -13.66, 172.24, "quake", "Oceania"),
    (6, "NHS LAUNCHES WORLD'S LARGEST AI TRIAL",
     "700,000 women at 30 sites will join the \u00a311m EDIT trial, testing "
     "whether AI can spot cancers earlier than the current programme.",
     "CONFIRMED — BBC", 52.20, 0.12, "ai", "Europe"),
    (7, "NEPAL PM BALEN SHAH WELCOMED IN DELHI",
     "The rapper-turned-prime minister began his first bilateral visit "
     "since taking office in March, with trade and power deals on the "
     "agenda.",
     "CONFIRMED — THE HINDU", 28.61, 77.21, "handshake", "South Asia"),
    (8, "NATO INTEL: RUSSIA PLANS NUCLEAR SATELLITE",
     "German media report NATO intelligence has concluded Russia plans to "
     "launch a satellite armed with a nuclear weapon into space this year.",
     "REPORTED — GERMAN MEDIA", 52.52, 13.40, "satellite", "Europe"),
    (9, "BOY, 7, PULLED ALIVE FROM RUBBLE IN DYMER",
     "Rescuers freed the boy after nearly 14 hours under rubble; the toll "
     "in Dymer rose to 11, with at least 15 dead across the Kyiv region.",
     "CONFIRMED — REUTERS", 50.78, 30.31, "rescue", "Europe"),
    (10, "ODESA SCHOOLS GO REMOTE AS GRID LIES IN RUINS",
     "All Odesa schools switch to remote learning from 23 to 27 November "
     "after Russian strikes wrecked the power grid, leaving 135,000 "
     "without power.",
     "REPORTED — FRANCE 24", 46.48, 30.72, "school", "Europe"),
    (11, "INDIA, CHINA OPEN 10 DAYS OF BORDER TALKS",
     "Negotiators began talks on the disputed frontier in Arunachal Pradesh "
     "in the first such meeting in years.",
     "CONFIRMED — THE HINDU", 28.00, 94.50, "border", "South Asia"),
    (12, "ARMY TO DETONATE AZIDE DESPITE PAUSE",
     "The US Army will destroy 68 barrels of the volatile explosive at an "
     "Iowa plant, days after a judge paused the plan over safety fears.",
     "CONFIRMED — AP", 40.83, -91.26, "barrel", "North America"),
    (13, "GAZA A \u2018TOXIC WASTELAND\u2019, OXFAM WARNS",
     "Indicators of toxic contamination cover more than 99% of Gaza and "
     "78% of its land is affected, a new Oxfam report says, warning of "
     "long-term harm to soil and water.",
     "CONFIRMED — OXFAM", 31.50, 34.47, "warning", "Middle East"),
    (14, "FRENCH PUPILS TO MARCH NATIONWIDE",
     "Pupils prepare to march against education reforms; student leaders "
     "met government officials on Monday as protests continue.",
     "REPORTED — FRENCH MEDIA", 48.86, 2.35, "protest", "Europe"),
    (15, "META AI CHIEF: AI MAY SOON BEAT HUMANS",
     "Alexandr Wang said superintelligence may soon surpass humans in every "
     "field; on Monday he added the takeover is not inevitable.",
     "REPORTED — AL JAZEERA", 37.45, -122.18, "robot", "North America"),
    (16, "SELANGOR FLOOD EVACUEES FALL TO 1,594",
     "The number of people in relief centres in Selangor dropped to 1,594 "
     "as floodwaters receded across the state.",
     "CONFIRMED — SELANGOR", 3.07, 101.52, "flood", "Southeast Asia"),
]

# (num, headline, deck, tag, lat, lon, region)
BRIEFS = [
    (17, "MAYON STAYS AT ALERT LEVEL 3",
     "PHIVOLCS' 23 Nov update keeps the Mayon alert at Level 3 as "
     "volcanic unrest continues.",
     "CONFIRMED — PHIVOLCS", 13.26, 123.69, "Southeast Asia"),
    (18, "ALBANIA: COP31 FAILURE A SIGN OF STRAIN",
     "Albania's delegation said the collapsed climate talks reflect the "
     "geopolitical strains on global cooperation.",
     "REPORTED — BALKAN WEB", 41.33, 19.82, "Europe"),
    (19, "1,389 INDIAN CHILDREN IN US CUSTODY",
     "US data show 1,389 unaccompanied Indian children entered custody "
     "since 2023, most arriving alone at the border.",
     "CONFIRMED — US GOVT", 38.91, -77.04, "North America"),
    (20, "KOSPI SLIDES 3.76%, SEOUL READIES FUND",
     "South Korea's Kospi fell 3.76% in early trade as officials prepare a "
     "10tn won fund to steady the market.",
     "CONFIRMED — REUTERS", 37.57, 126.98, "East Asia"),
    (21, "CHINA TO CUT STOCK MARGIN RATIO TO 80%",
     "China will lower the stock-margin ratio to 80% from 30 November in a "
     "bid to cool leveraged trading.",
     "CONFIRMED — REUTERS", 39.90, 116.41, "East Asia"),
    (22, "IRAN VOWS \u2018ALL MEANS\u2019 AGAINST BLOCKADE",
     "Iran's foreign ministry says it will use all available means to "
     "counter the US naval blockade and defend itself.",
     "REPORTED — AL JAZEERA", 35.69, 51.39, "Middle East"),
    (23, "SEOUL FILES CASES IN AI EXAM SCANDAL",
     "Five people face criminal cases over AI-assisted cheating in "
     "South Korea's national college entrance exam.",
     "CONFIRMED — KOREA HERALD", 37.57, 126.98, "East Asia"),
    (24, "MLA WRITES LETTER IN BLOOD, DETAINED",
     "A Congress MLA wrote to Haryana's chief minister in blood over "
     "unpaid wages and was briefly detained.",
     "CONFIRMED — THE HINDU", 30.73, 76.78, "South Asia"),
    (25, "BJP PROTESTS OVER BANGLADESH ATTACKS",
     "The BJP announced protests in West Bengal over attacks on Hindus in "
     "Bangladesh.",
     "REPORTED — THE HINDU", 22.57, 88.36, "South Asia"),
    (26, "REGULATOR ORDERS BISLERI PROSECUTION",
     "India's food regulator ordered prosecution of Bisleri over unsafe "
     "drinking water found in tests.",
     "CONFIRMED — THE HINDU", 28.63, 77.23, "South Asia"),
    (27, "ENERGY BILLS TO SOAR, HOUSEHOLDS WARNED",
     "Households face sharply higher energy bills this winter, consumer "
     "groups warned.",
     "REPORTED — UK MEDIA", 51.51, -0.13, "Europe"),
    (28, "TYSON FURY REVEALS SCHIZOPHRENIA DIAGNOSIS",
     "The former heavyweight champion spoke about his schizophrenia "
     "diagnosis in a new documentary.",
     "CONFIRMED — BBC", 53.48, -2.24, "Europe"),
    (29, "COMPASS TO MOVE LISTING TO NEW YORK",
     "Estate agency Compass will move its stock-market listing from London "
     "to New York.",
     "CONFIRMED — LSE FILING", 51.39, -0.51, "Europe"),
    (30, "UK PLANS UNIVERSAL-CREDIT REFORM",
     "Ministers plan universal-credit reform to push more people into "
     "work, with new conditions for claimants.",
     "REPORTED — UK MEDIA", 51.50, -0.12, "Europe"),
    (31, "DISABILITY REVIEW TO RECOMMEND CHANGES",
     "A review of disability benefits will recommend changes to payments, "
     "ministers signalled.",
     "REPORTED — UK MEDIA", 51.52, -0.14, "Europe"),
    (32, "SINDAROV GETS WHITE PIECES FOR GAME 1",
     "Javokhir Sindarov will play white in Tuesday's opening game of the "
     "World Championship match.",
     "CONFIRMED — FIDE", 46.20, 6.14, "Europe"),
    (33, "CAMARA STAYS WITH HAAS FOR FINAL RACES",
     "The Brazilian will drive for Haas in the final two grands prix of "
     "the season.",
     "CONFIRMED — HAAS F1", 35.49, -80.62, "North America"),
    (34, "US INTEL CHIEF TRUSTS TRUMP'S \u2018MY WAY\u2019 LINE",
     "The US intelligence chief said she trusts the president's "
     "description of his approach to allies.",
     "REPORTED — US MEDIA", 38.90, -77.03, "North America"),
    (35, "FIFA CONFIRMS UK AS 2035 WOMEN'S CUP HOST",
     "FIFA confirmed the UK will host the 2035 Women's World Cup, with 48 "
     "teams and 104 matches at 19 venues.",
     "CONFIRMED — FIFA", 47.38, 8.54, "Europe"),
    (36, "POCHETTINO DEMANDS RESPONSE AFTER 4-0",
     "The US coach demanded a response from his players after Manchester "
     "United's 4-0 defeat at Anfield.",
     "REPORTED — US MEDIA", 53.47, -2.23, "Europe"),
    (37, "SYED MODI BADMINTON BUILD-UP IN LUCKNOW",
     "The Syed Modi India International badminton tournament begins its "
     "build-up in Lucknow.",
     "CONFIRMED — BAI", 26.85, 80.95, "South Asia"),
    (38, "ANTI-GRAFT BODY TO HEAR GOLD-BRIBE CASE",
     "Thailand's anti-graft body will hear a case over gold allegedly "
     "offered as a bribe.",
     "REPORTED — THAI MEDIA", 13.76, 100.50, "Southeast Asia"),
    (39, "POLICE PROBE REMAINS FOUND IN BANGKOK",
     "Police are investigating human remains found in Bangkok, with "
     "forensic teams at the scene.",
     "REPORTED — THAI MEDIA", 13.75, 100.52, "Southeast Asia"),
]

# Region bar: (label, count) — sums to 39.
REGIONS = [
    ("EUROPE", 15), ("EAST ASIA", 4), ("SOUTH ASIA", 6),
    ("SOUTHEAST ASIA", 4), ("NORTH AMERICA", 5), ("MIDDLE EAST", 2),
    ("AFRICA", 1), ("OCEANIA", 2),
]

# Stat strip: (big, caption) — each from a different non-hero story.
STATS = [
    ("6.5", "MAGNITUDE, VANUATU QUAKE"),
    ("700,000", "WOMEN IN NHS AI TRIAL"),
    ("48", "TEAMS AT 2035 WORLD CUP"),
    ("1,594", "FLOOD EVACUEES, SELANGOR"),
    ("10", "DAYS OF INDIA-CHINA TALKS"),
    ("99%", "OF GAZA CONTAMINATED"),
]

# DATE CHECK: near-miss stories from other days, excluded from the front page.
DATECHECK = [
    "COP31 climate talks collapse \u2014 Sun 22 Nov",
    "Democrats' 258 House seats \u2014 Sun 22 Nov",
    "Paredes collapses on live TV \u2014 Sat 21 Nov",
    "Denmark expels Russian attach\u00e9 \u2014 Fri 20",
    "China warns off Fuji climbs \u2014 Tue 17 Nov",
    "Hormuz tanker strikes \u2014 Fri\u2013Sat 20\u201321 Nov",
    "Barcelona 3\u20132 Villarreal \u2014 Sun 22 Nov",
    "Liverpool 4\u20130 Man Utd \u2014 Sun 22 Nov",
]

# Map pins: (num, lat, lon) — every story has a true-location pin.
PINS = [(n, lat, lon) for (n, _, _, _, lat, lon, _) in HEROES]
PINS += [(n, lat, lon) for (n, _, _, _, lat, lon, _, _) in MIDS]
PINS += [(n, lat, lon) for (n, _, _, _, lat, lon, _) in BRIEFS]

# ---------------------------------------------------------------- illustrations
def art_ship(d, x0, y0, x1, y1):
    """Warship under a night sky, drones above."""
    d.rectangle([x0, y0, x1, y1], fill=(24, 38, 62))
    rng = random.Random(11)
    for _ in range(26):
        d.point((rng.randrange(x0 + 4, x1 - 4), rng.randrange(y0 + 4, y0 + 30)),
                fill=(240, 236, 210))
    d.ellipse([x0 + 18, y0 + 14, x0 + 34, y0 + 30], fill=(222, 200, 120))
    # sea
    d.rectangle([x0, y1 - 26, x1, y1], fill=(42, 80, 112))
    for yy in range(y1 - 22, y1 - 2, 6):
        d.line([(x0 + 6, yy), (x0 + 30, yy)], fill=(150, 190, 210), width=2)
        d.line([(x0 + 44, yy + 3), (x0 + 70, yy + 3)], fill=(150, 190, 210), width=2)
    # hull
    d.polygon([(x0 + 16, y1 - 34), (x0 + 84, y1 - 34), (x0 + 78, y1 - 26),
               (x0 + 22, y1 - 26)], fill=(96, 96, 100))
    d.rectangle([x0 + 34, y1 - 52, x0 + 52, y1 - 34], fill=(120, 122, 126))
    d.line([(x0 + 42, y1 - 52), (x0 + 42, y1 - 64)], fill=(200, 200, 200), width=2)
    d.polygon([(x0 + 42, y1 - 64), (x0 + 42, y1 - 54), (x0 + 58, y1 - 56)],
              fill=(158, 28, 28))
    # drones
    for dx, dy in ((x0 + 12, y0 + 12), (x0 + 78, y0 + 10), (x0 + 90, y0 + 24)):
        d.ellipse([dx - 3, dy - 2, dx + 3, dy + 2], fill=(230, 230, 230))
        d.line([(dx - 6, dy - 3), (dx + 6, dy - 3)], fill=(200, 200, 200), width=1)
    # smoke plume
    d.ellipse([x0 + 66, y1 - 62, x0 + 82, y1 - 44], fill=(200, 200, 200))
    d.ellipse([x0 + 72, y1 - 74, x0 + 86, y1 - 58], fill=(210, 210, 210))


def art_chart(d, x0, y0, x1, y1):
    """Market chart: falling then rising, with a red ban slash."""
    d.rectangle([x0, y0, x1, y1], fill=(238, 240, 236))
    for i in range(5):
        yy = y0 + 14 + i * 16
        d.line([(x0 + 6, yy), (x1 - 6, yy)], fill=(214, 220, 214), width=1)
    pts = [(x0 + 8, y0 + 34), (x0 + 24, y0 + 44), (x0 + 40, y0 + 58),
           (x0 + 56, y0 + 48), (x0 + 72, y0 + 30), (x0 + 88, y0 + 18)]
    d.line(pts, fill=(38, 92, 50), width=3)
    d.line(pts, fill=(158, 28, 28), width=1)
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(26, 24, 20))
    # ban circle
    d.ellipse([x0 + 66, y0 + 52, x0 + 98, y0 + 84], outline=(158, 28, 28), width=3)
    d.line([(x0 + 71, y0 + 79), (x0 + 93, y0 + 57)], fill=(158, 28, 28), width=3)


def art_star(d, x0, y0, x1, y1):
    """NATO compass star on deep blue."""
    d.rectangle([x0, y0, x1, y1], fill=(31, 58, 95))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    R, r = 34, 12
    for k in range(4):
        ang = math.pi / 2 + k * math.pi / 2
        tip = (cx + R * math.cos(ang), cy - R * math.sin(ang))
        left = (cx + r * math.cos(ang + 0.45), cy - r * math.sin(ang + 0.45))
        right = (cx + r * math.cos(ang - 0.45), cy - r * math.sin(ang - 0.45))
        d.polygon([tip, left, right], fill=(226, 232, 240))
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=(226, 232, 240), width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(222, 200, 120))


def art_cricket(d, x0, y0, x1, y1):
    """Cricket bat, ball and stumps on green."""
    d.rectangle([x0, y0, x1, y1], fill=(214, 230, 196))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(38, 92, 50))
    # stumps
    for sx in (x0 + 14, x0 + 20, x0 + 26):
        d.rectangle([sx, y0 + 22, sx + 3, y0 + 48], fill=(222, 200, 120))
    d.rectangle([x0 + 14, y0 + 19, x0 + 29, y0 + 22], fill=(222, 200, 120))
    # bat
    d.polygon([(x0 + 62, y0 + 18), (x0 + 74, y0 + 18), (x0 + 70, y0 + 62),
               (x0 + 58, y0 + 62)], fill=(222, 200, 120))
    d.rectangle([x0 + 64, y0 + 8, x0 + 70, y0 + 20], fill=(96, 72, 40))
    # ball
    d.ellipse([x0 + 82, y0 + 30, x0 + 92, y0 + 40], fill=(158, 28, 28))
    d.arc([x0 + 82, y0 + 30, x0 + 92, y0 + 40], 20, 160, fill=(250, 246, 236), width=1)


def art_quake(d, x0, y0, x1, y1):
    """Seismic waves over a fault line."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 240))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for rr, col in ((30, (158, 28, 28)), (22, (31, 58, 95)), (14, (26, 24, 20))):
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(158, 28, 28))
    d.line([(x0 + 8, y1 - 14), (x0 + 30, y1 - 22), (x0 + 52, y1 - 12),
            (x0 + 74, y1 - 20), (x1 - 8, y1 - 14)], fill=(120, 110, 90), width=2)


def art_ai(d, x0, y0, x1, y1):
    """AI circuit head / neural net."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 240))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # nodes
    nodes = [(x0 + 16, y0 + 16), (x0 + 50, y0 + 12), (x0 + 84, y0 + 18),
             (x0 + 14, y0 + 42), (x0 + 50, y0 + 38), (x0 + 86, y0 + 44),
             (x0 + 18, y0 + 68), (x0 + 52, y0 + 64), (x0 + 82, y0 + 66)]
    for a in nodes:
        for b in nodes:
            if a != b and abs(a[0] - b[0]) < 40 and abs(a[1] - b[1]) < 30:
                d.line([a, b], fill=(150, 170, 200), width=1)
    for nx, ny in nodes:
        d.ellipse([nx - 4, ny - 4, nx + 4, ny + 4], fill=(31, 58, 95))
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(158, 28, 28))


def art_handshake(d, x0, y0, x1, y1):
    """Two flags meeting over a table."""
    d.rectangle([x0, y0, x1, y1], fill=(238, 230, 208))
    d.rectangle([x0, y1 - 18, x1, y1], fill=(120, 84, 48))
    # left flag (saffron/white/green)
    d.polygon([(x0 + 12, y0 + 10), (x0 + 40, y0 + 16), (x0 + 12, y0 + 22)],
              fill=(255, 153, 51))
    d.polygon([(x0 + 12, y0 + 22), (x0 + 40, y0 + 16), (x0 + 40, y0 + 24),
               (x0 + 12, y0 + 30)], fill=(250, 246, 236))
    d.polygon([(x0 + 12, y0 + 30), (x0 + 40, y0 + 24), (x0 + 12, y0 + 36)],
              fill=(19, 136, 8))
    d.line([(x0 + 12, y0 + 10), (x0 + 12, y0 + 62)], fill=(60, 56, 48), width=2)
    # right flag (crimson/blue)
    d.polygon([(x1 - 12, y0 + 10), (x1 - 40, y0 + 16), (x1 - 12, y0 + 22)],
              fill=(220, 20, 60))
    d.polygon([(x1 - 12, y0 + 22), (x1 - 40, y0 + 16), (x1 - 40, y0 + 24),
               (x1 - 12, y0 + 30)], fill=(0, 56, 147))
    d.polygon([(x1 - 12, y0 + 30), (x1 - 40, y0 + 24), (x1 - 12, y0 + 36)],
              fill=(220, 20, 60))
    d.line([(x1 - 12, y0 + 10), (x1 - 12, y0 + 62)], fill=(60, 56, 48), width=2)
    # clasped hands
    d.ellipse([x0 + 34, y0 + 48, x0 + 66, y0 + 66], fill=(222, 184, 150))
    d.line([(x0 + 40, y0 + 56), (x0 + 60, y0 + 56)], fill=(180, 140, 110), width=2)


def art_satellite(d, x0, y0, x1, y1):
    """Satellite with solar panels in orbit."""
    d.rectangle([x0, y0, x1, y1], fill=(18, 26, 44))
    rng = random.Random(23)
    for _ in range(20):
        d.point((rng.randrange(x0 + 4, x1 - 4), rng.randrange(y0 + 4, y1 - 4)),
                fill=(240, 236, 210))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.ellipse([x0 + 8, y0 + 52, x0 + 96, y0 + 76], outline=(100, 120, 150), width=1)
    # panels
    d.rectangle([x0 + 10, cy - 8, x0 + 34, cy + 8], fill=(31, 58, 95),
                outline=(150, 170, 200))
    d.rectangle([x0 + 66, cy - 8, x0 + 90, cy + 8], fill=(31, 58, 95),
                outline=(150, 170, 200))
    for px in (x0 + 16, x0 + 22, x0 + 28):
        d.line([(px, cy - 8), (px, cy + 8)], fill=(150, 170, 200), width=1)
    for px in (x0 + 72, x0 + 78, x0 + 84):
        d.line([(px, cy - 8), (px, cy + 8)], fill=(150, 170, 200), width=1)
    # body
    d.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], fill=(200, 200, 200),
                outline=(120, 120, 120))
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(158, 28, 28))
    d.line([(cx, cy - 12), (cx, cy - 22)], fill=(200, 200, 200), width=2)
    d.ellipse([cx - 2, cy - 24, cx + 2, cy - 20], fill=(222, 200, 120))


def art_rescue(d, x0, y0, x1, y1):
    """Rescuer reaching into rubble."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 220, 200))
    # rubble
    for rx, ry, rw, rh in ((x0 + 8, y1 - 22, 26, 12), (x0 + 36, y1 - 16, 30, 10),
                           (x0 + 68, y1 - 24, 24, 14), (x0 + 22, y1 - 34, 20, 10)):
        d.rectangle([rx, ry, rx + rw, ry + rh], fill=(150, 138, 112))
        d.line([(rx, ry), (rx + rw, ry + rh)], fill=(110, 102, 86), width=1)
    # rescuer arm + helmet
    d.ellipse([x0 + 34, y0 + 14, x0 + 66, y0 + 40], fill=(222, 200, 120))
    d.arc([x0 + 34, y0 + 14, x0 + 66, y0 + 40], 180, 360, fill=(158, 28, 28), width=4)
    d.polygon([(x0 + 44, y0 + 40), (x0 + 56, y0 + 40), (x0 + 50, y0 + 58)],
              fill=(222, 184, 150))
    d.ellipse([x0 + 46, y0 + 56, x0 + 54, y0 + 64], fill=(222, 184, 150))


def art_flood(d, x0, y0, x1, y1):
    """Flooded street with rooftops and rain."""
    d.rectangle([x0, y0, x1, y1], fill=(120, 130, 140))
    for xx in range(x0 + 6, x1 - 6, 14):
        d.line([(xx, y0 + 6), (xx - 4, y0 + 16)], fill=(200, 210, 220), width=1)
    # rooftops
    d.polygon([(x0 + 8, y0 + 44), (x0 + 28, y0 + 28), (x0 + 48, y0 + 44)],
              fill=(158, 28, 28))
    d.polygon([(x0 + 52, y0 + 44), (x0 + 72, y0 + 28), (x0 + 92, y0 + 44)],
              fill=(31, 58, 95))
    # water
    d.rectangle([x0, y0 + 44, x1, y1], fill=(42, 80, 112))
    for yy in range(y0 + 50, y1 - 4, 8):
        d.line([(x0 + 8, yy), (x0 + 30, yy)], fill=(150, 190, 210), width=2)
        d.line([(x0 + 44, yy + 4), (x0 + 70, yy + 4)], fill=(150, 190, 210), width=2)
    # floating debris
    d.rectangle([x0 + 60, y0 + 56, x0 + 78, y0 + 62], fill=(120, 84, 48))


def art_school(d, x0, y0, x1, y1):
    """Schoolhouse with a flag, one dark window for the power cut."""
    d.rectangle([x0, y0, x1, y1], fill=(214, 226, 232))
    # roof
    d.polygon([(x0 + 12, y0 + 36), (x0 + 50, y0 + 12), (x0 + 88, y0 + 36)],
              fill=(158, 28, 28))
    # walls
    d.rectangle([x0 + 16, y0 + 36, x0 + 84, y0 + 68], fill=(232, 220, 196))
    # door
    d.rectangle([x0 + 44, y0 + 48, x0 + 56, y0 + 68], fill=(90, 60, 30))
    # windows (left dark = power cut, right lit)
    d.rectangle([x0 + 22, y0 + 42, x0 + 34, y0 + 52], fill=(40, 40, 48))
    d.rectangle([x0 + 66, y0 + 42, x0 + 78, y0 + 52], fill=(120, 160, 190))
    # flag
    d.line([(x0 + 50, y0 + 12), (x0 + 50, y0 + 2)], fill=(60, 56, 48), width=2)
    d.polygon([(x0 + 50, y0 + 2), (x0 + 64, y0 + 6), (x0 + 50, y0 + 10)],
              fill=(31, 58, 95))


def art_border(d, x0, y0, x1, y1):
    """Mountain pass with a dashed frontier line."""
    d.rectangle([x0, y0, x1, y1], fill=(214, 226, 232))
    d.polygon([(x0, y1 - 20), (x0 + 30, y0 + 14), (x0 + 60, y1 - 20)],
              fill=(120, 130, 140))
    d.polygon([(x0 + 40, y1 - 20), (x0 + 72, y0 + 8), (x1, y1 - 20)],
              fill=(100, 112, 124))
    d.polygon([(x0 + 26, y0 + 18), (x0 + 30, y0 + 14), (x0 + 34, y0 + 18),
               (x0 + 30, y0 + 22)], fill=(250, 246, 236))
    d.polygon([(x0 + 68, y0 + 12), (x0 + 72, y0 + 8), (x0 + 76, y0 + 12),
               (x0 + 72, y0 + 16)], fill=(250, 246, 236))
    d.rectangle([x0, y1 - 20, x1, y1], fill=(38, 92, 50))
    for xx in range(x0 + 4, x1 - 4, 12):
        d.line([(xx, y1 - 10), (xx + 6, y1 - 10)], fill=(250, 246, 236), width=2)


def art_barrel(d, x0, y0, x1, y1):
    """Hazard barrels with a warning triangle."""
    d.rectangle([x0, y0, x1, y1], fill=(238, 230, 208))
    for bx in (x0 + 10, x0 + 40, x0 + 70):
        d.rectangle([bx, y0 + 30, bx + 24, y0 + 70], fill=(176, 132, 40),
                    outline=(120, 84, 40))
        d.line([(bx, y0 + 40), (bx + 24, y0 + 40)], fill=(120, 84, 40), width=2)
        d.line([(bx, y0 + 58), (bx + 24, y0 + 58)], fill=(120, 84, 40), width=2)
    # warning triangle
    cx = (x0 + x1) // 2
    d.polygon([(cx, y0 + 8), (cx + 12, y0 + 26), (cx - 12, y0 + 26)],
              fill=(222, 200, 120), outline=(158, 28, 28))
    d.text((cx - 2, y0 + 13), "!", font=font(F_SANS_B, 11), fill=(158, 28, 28))


def art_warning(d, x0, y0, x1, y1):
    """Biohazard-style warning over cracked ground."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 220, 196))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 6
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(222, 200, 120),
              outline=(158, 28, 28))
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(158, 28, 28))
    for ang in (90, 210, 330):
        a = math.radians(ang)
        x2 = cx + 18 * math.cos(a)
        y2 = cy - 18 * math.sin(a)
        d.pieslice([x2 - 8, y2 - 8, x2 + 8, y2 + 8], 0, 360, fill=(158, 28, 28))
    # cracks
    d.line([(x0 + 10, y1 - 10), (x0 + 34, y1 - 20), (x0 + 52, y1 - 12)],
           fill=(110, 102, 86), width=2)
    d.line([(x1 - 10, y1 - 8), (x1 - 30, y1 - 18), (x1 - 50, y1 - 12)],
           fill=(110, 102, 86), width=2)


def art_protest(d, x0, y0, x1, y1):
    """Marchers with placards."""
    d.rectangle([x0, y0, x1, y1], fill=(238, 236, 228))
    # placards
    d.rectangle([x0 + 10, y0 + 10, x0 + 36, y0 + 30], fill=(250, 246, 236),
                outline=(26, 24, 20))
    d.line([(x0 + 22, y0 + 16), (x0 + 30, y0 + 16)], fill=(158, 28, 28), width=2)
    d.line([(x0 + 20, y0 + 22), (x0 + 32, y0 + 22)], fill=(26, 24, 20), width=2)
    d.rectangle([x0 + 62, y0 + 8, x0 + 88, y0 + 28], fill=(250, 246, 236),
                outline=(26, 24, 20))
    d.line([(x0 + 70, y0 + 14), (x0 + 80, y0 + 14)], fill=(31, 58, 95), width=2)
    d.line([(x0 + 68, y0 + 20), (x0 + 82, y0 + 20)], fill=(26, 24, 20), width=2)
    # heads + shoulders
    for hx in (x0 + 22, x0 + 50, x0 + 76):
        d.ellipse([hx - 6, y0 + 34, hx + 6, y0 + 46], fill=(222, 184, 150))
        d.pieslice([hx - 12, y0 + 46, hx + 12, y0 + 74], 180, 360,
                   fill=(31, 58, 95))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(120, 110, 90))


def art_robot(d, x0, y0, x1, y1):
    """Robot head with glowing eyes."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 240))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # antenna
    d.line([(cx, y0 + 10), (cx, y0 + 20)], fill=(60, 56, 48), width=2)
    d.ellipse([cx - 3, y0 + 6, cx + 3, y0 + 12], fill=(158, 28, 28))
    # head
    d.rounded_rectangle([cx - 26, y0 + 20, cx + 26, y0 + 56], radius=8,
                        fill=(200, 206, 212), outline=(60, 56, 48))
    d.ellipse([cx - 16, y0 + 30, cx - 6, y0 + 40], fill=(158, 28, 28))
    d.ellipse([cx + 6, y0 + 30, cx + 16, y0 + 40], fill=(158, 28, 28))
    for yy in range(y0 + 46, y0 + 54, 3):
        d.line([(cx - 12, yy), (cx + 12, yy)], fill=(60, 56, 48), width=1)
    # ears
    d.rectangle([cx - 32, y0 + 30, cx - 26, y0 + 46], fill=(120, 124, 130))
    d.rectangle([cx + 26, y0 + 30, cx + 32, y0 + 46], fill=(120, 124, 130))


ART = {
    "ship": art_ship, "chart": art_chart, "star": art_star,
    "cricket": art_cricket, "quake": art_quake, "ai": art_ai,
    "handshake": art_handshake, "satellite": art_satellite,
    "rescue": art_rescue, "flood": art_flood, "border": art_border,
    "barrel": art_barrel, "warning": art_warning, "protest": art_protest,
    "robot": art_robot, "school": art_school,
}


_IMG = None  # page image, set by render(); used by art_for to paste art


def art_for(kind, d, x0, y0, x1, y1):
    """Render one illustration into a 100x76 temp, then paste it into the
    target box aspect-preserved (letterboxed on the newsprint paper)."""
    tmp = Image.new("RGB", (100, 76), PAPER)
    td = ImageDraw.Draw(tmp)
    ART[kind](td, 0, 0, 100, 76)
    bw, bh = int(x1 - x0), int(y1 - y0)
    scale = min(bw / 100.0, bh / 76.0)
    nw = max(1, int(100 * scale))
    nh = max(1, int(76 * scale))
    tmp = tmp.resize((nw, nh), Image.LANCZOS)
    _IMG.paste(tmp, (int(x0 + (bw - nw) / 2), int(y0 + (bh - nh) / 2)))
    d.rectangle([x0, y0, x1, y1], outline=(150, 138, 112), width=1)

# ---------------------------------------------------------------- world map
MAP = dict(x0=14, y0=0, x1=1010, y1=0)  # y0/y1 set by the caller
MAP_LON0, MAP_LON1 = -180.0, 180.0
MAP_LAT0, MAP_LAT1 = -58.0, 84.0
# Sea whitelisted: (num, label) — pins that legitimately sit on water.
SEA_PINS = {5: "QUAKE AT SEA OFF VANUATU"}


def lonlat_to_xy(lon, lat, mx0, my0, mx1, my1):
    fx = (lon - MAP_LON0) / (MAP_LON1 - MAP_LON0)
    fy = (MAP_LAT1 - lat) / (MAP_LAT1 - MAP_LAT0)
    return mx0 + fx * (mx1 - mx0), my0 + fy * (my1 - my0)


def point_in_poly(px, py, poly):
    """Ray-casting point-in-polygon (poly in pixel coords)."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (
                px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_map_land(d, mx0, my0, mx1, my1):
    """Paint the sea, then every continent polygon in map coords."""
    d.rectangle([mx0, my0, mx1, my1], fill=SEA)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, mx0, my0, mx1, my1) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)


def point_on_land(lat, lon, mx0, my0, mx1, my1):
    px, py = lonlat_to_xy(lon, lat, mx0, my0, mx1, my1)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lo, la, mx0, my0, mx1, my1) for lo, la in poly]
        if point_in_poly(px, py, pts):
            return True
    return False


def seg_hits_rect(x1, y1, x2, y2, rx0, ry0, rx1, ry1):
    """True if segment (x1,y1)-(x2,y2) touches rect [rx0,ry0,rx1,ry1]."""
    def inside(px, py):
        return rx0 <= px <= rx1 and ry0 <= py <= ry1

    if inside(x1, y1) or inside(x2, y2):
        return True

    def seg_int(ax, ay, bx, by, cx, cy, dx, dy):
        den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
        if den == 0:
            return False
        t = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den
        u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
        return 0 <= t <= 1 and 0 <= u <= 1

    edges = [((rx0, ry0), (rx1, ry0)), ((rx1, ry0), (rx1, ry1)),
             ((rx1, ry1), (rx0, ry1)), ((rx0, ry1), (rx0, ry0))]
    for (ax, ay), (bx, by) in edges:
        if seg_int(x1, y1, x2, y2, ax, ay, bx, by):
            return True
    return False


def solve_badges(dots):
    """Place numbered badges around map dots.

    dots: list of (num, x, y) in pixel coords. Returns list of
    (num, bx0, by0, bx1, by1) badge boxes (20x14). Constraints:
    - badge box stays inside the map frame
    - badge boxes never overlap each other
    - badge box never covers any dot
    - a leader segment (dot -> badge centre) never crosses any OTHER badge
    Most-constrained dots are placed first; radius grows on failure.
    """
    bw, bh = 14, 11
    # order: dots with the most neighbours within 60px go first
    def neighbours(i):
        xi, yi = dots[i][1], dots[i][2]
        return sum(1 for j, (_, xj, yj) in enumerate(dots)
                   if j != i and abs(xj - xi) < 60 and abs(yj - yi) < 60)

    # order: outermost dots of each cluster first (their outward slots are
    # the ones inner dots would otherwise block), then by neighbour count
    def local_centroid(i):
        near = [j for j in range(len(dots))
                if abs(dots[j][1] - dots[i][1]) < 90
                and abs(dots[j][2] - dots[i][2]) < 60]
        gx = sum(dots[j][1] for j in near) / len(near)
        gy = sum(dots[j][2] for j in near) / len(near)
        return gx, gy

    def dist_from_centroid(i):
        gx, gy = local_centroid(i)
        return math.hypot(dots[i][1] - gx, dots[i][2] - gy)

    order = sorted(range(len(dots)),
                   key=lambda i: (-dist_from_centroid(i), -neighbours(i)))
    placed = {}  # index -> (bx0, by0, bx1, by1)
    leaders = {}  # index -> (dot_x, dot_y, badge_cx, badge_cy)

    def candidate_ok(idx, cx, cy):
        bx0, by0 = cx - bw / 2, cy - bh / 2
        bx1, by1 = bx0 + bw, by0 + bh
        if bx0 < MAP["x0"] + 1 or by0 < MAP["y0"] + 1:
            return False
        if bx1 > MAP["x1"] - 1 or by1 > MAP["y1"] - 1:
            return False
        for j, (px0, py0, px1, py1) in placed.items():
            if not (bx1 <= px0 or bx0 >= px1 or by1 <= py0 or by0 >= py1):
                return False  # overlap with another badge
        dx, dy = dots[idx][1], dots[idx][2]
        for (_, jx, jy) in dots:
            if bx0 - 2 <= jx <= bx1 + 2 and by0 - 2 <= jy <= by1 + 2:
                return False  # covers a dot
        # leader from this dot to the badge centre must not cross a badge
        bcx, bcy = (bx0 + bx1) / 2, (by0 + by1) / 2
        for j, (px0, py0, px1, py1) in placed.items():
            if seg_hits_rect(dx, dy, bcx, bcy, px0, py0, px1, py1):
                return False
        # the new badge must not sit on an existing leader either
        for j, (lx0, ly0, lx1, ly1) in leaders.items():
            if seg_hits_rect(lx0, ly0, lx1, ly1, bx0, by0, bx1, by1):
                return False
        return True

    def store(idx, cx, cy):
        placed[idx] = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
        leaders[idx] = (dots[idx][1], dots[idx][2], cx, cy)

    def place(idx):
        _, dx, dy = dots[idx]
        # try rings of increasing radius, 24 directions each; fine steps
        # matter — the Europe cluster has usable gaps only a few px wide
        for radius in (24, 28, 32, 36, 40, 46, 52, 60, 70, 82, 96, 112,
                       130, 150):
            for k in range(24):
                ang = k * math.pi / 12
                cx = dx + radius * math.cos(ang)
                cy = dy + radius * math.sin(ang) * 0.8
                if candidate_ok(idx, cx, cy):
                    store(idx, cx, cy)
                    return True
        return False

    def place_radial(idx, group):
        """Cluster fallback: try the dot's own outward direction from the
        group's centroid first (leaders radiate out, crossing nothing),
        then evenly-spaced slots around the centroid."""
        gx = sum(dots[i][1] for i in group) / len(group)
        gy = sum(dots[i][2] for i in group) / len(group)
        ordered = sorted(group,
                         key=lambda i: math.atan2(dots[i][2] - gy,
                                                  dots[i][1] - gx))
        slot = ordered.index(idx)
        slot_ang = slot * 2 * math.pi / max(1, len(ordered))
        _, dx, dy = dots[idx]
        radial = math.atan2(dy - gy, dx - gx)
        for radius in (36, 44, 52, 60, 70, 82, 96, 112, 130, 150, 190, 240):
            for ang in (radial, radial + 0.15, radial - 0.15,
                        radial + 0.3, radial - 0.3, radial + 0.5,
                        radial - 0.5, slot_ang,
                        slot_ang + 0.15, slot_ang - 0.15):
                cx = dx + radius * math.cos(ang)
                cy = dy + radius * math.sin(ang) * 0.8
                if candidate_ok(idx, cx, cy):
                    store(idx, cx, cy)
                    return True
        return False

    for idx in order:
        if not place(idx):
            # cluster fallback: group = unplaced dots near this one
            group = [j for j in range(len(dots))
                     if j not in placed and j != idx
                     and abs(dots[j][1] - dots[idx][1]) < 90
                     and abs(dots[j][2] - dots[idx][2]) < 60]
            group.append(idx)
            place_radial(idx, group)
    out = []
    for i, (num, _, _) in enumerate(dots):
        if i in placed:
            out.append((num,) + placed[i])
    return out


def verify_badges(dots, badges):
    """Return (overlaps, dots_covered, leader_crossings) for the placed set."""
    boxes = {num: (x0, y0, x1, y1) for num, x0, y0, x1, y1 in badges}
    overlaps = 0
    items = list(boxes.items())
    for a in range(len(items)):
        for b in range(a + 1, len(items)):
            (n1, (ax0, ay0, ax1, ay1)) = items[a]
            (n2, (bx0, by0, bx1, by1)) = items[b]
            if not (ax1 <= bx0 or ax0 >= bx1 or ay1 <= by0 or ay0 >= by1):
                overlaps += 1
    covered = 0
    for num, dx, dy in dots:
        for n2, (x0, y0, x1, y1) in boxes.items():
            if n2 != num and x0 - 2 <= dx <= x1 + 2 and y0 - 2 <= dy <= y1 + 2:
                covered += 1
    crossings = 0
    for num, dx, dy in dots:
        if num not in boxes:
            continue
        bx0, by0, bx1, by1 = boxes[num]
        bcx, bcy = (bx0 + bx1) / 2, (by0 + by1) / 2
        for n2, (px0, py0, px1, py1) in boxes.items():
            if n2 != num and seg_hits_rect(dx, dy, bcx, bcy, px0, py0, px1, py1):
                crossings += 1
    return overlaps, covered, crossings

# ---------------------------------------------------------------- layout
def fit_line(draw, text, fnt, width):
    """Truncate `text` with an ellipsis so it fits `width` px."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if draw.textlength(text[:mid] + ell, font=fnt) <= width:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo].rstrip() + ell


def wrap_n(draw, text, fnt, width, max_lines):
    """Wrap to at most `max_lines` lines; a cut is always marked with an
    ellipsis so a summary never ends mid-sentence without signalling it."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    last = out[-1]
    ell_w = draw.textlength("…", font=fnt)
    cut = fit_line(draw, last, fnt, width - ell_w)
    out[-1] = cut if cut.endswith("…") else cut + "…"
    return out


def num_chip(d, x, y, n, size=16):
    """Small red circle with a white story number."""
    d.ellipse([x, y, x + size, y + size], fill=ACCENT)
    f = font(F_SANS_B, 10 if size <= 16 else 12)
    t = str(n)
    tw = d.textlength(t, font=f)
    d.text((x + (size - tw) / 2, y + (size - f.size) / 2 - 1), t,
           font=f, fill=(250, 246, 236))


def draw_masthead(d):
    f_name = font(F_SERIF_B, 44)
    draw_centered(d, W // 2, 10, "THE WORLD IN ONE PAGE", f_name, INK)
    rule(d, 14, W - 14, 58, fill=INK, width=2)
    f_date = font(F_SANS_B, 11)
    draw_centered(d, W // 2, 63,
                  "MONDAY 23 NOVEMBER 2026  ·  39 STORIES FROM ONE DAY  ·  "
                  "EVERY DATE VERIFIED",
                  f_date, INK_SOFT)
    rule(d, 14, W - 14, 80, fill=RULE, width=1)


def draw_stats(d):
    y0, y1 = 84, 112
    x0, x1 = 14, W - 14
    n = len(STATS)
    cw = (x1 - x0) / n
    f_big = font(F_SERIF_B, 19)
    f_cap = font(F_SANS_B, 8)
    for i, (big, cap) in enumerate(STATS):
        cx = x0 + cw * i + cw / 2
        draw_centered(d, cx, y0 + 1, big, f_big, ACCENT_DK)
        draw_centered(d, cx, y0 + 22, cap, f_cap, MUTED)
        if i:
            d.line([(x0 + cw * i, y0 + 3), (x0 + cw * i, y1 - 3)],
                   fill=RULE, width=1)
    rule(d, x0, x1, y1 + 2, fill=INK, width=1)


def draw_heroes(d):
    y0 = 120
    x0, x1 = 14, W - 14
    cw = (x1 - x0 - 20) // 3
    f_head = font(F_SERIF_B, 14)
    f_deck = font(F_SANS, 10)
    for i, (n, head, deck, tagtxt, lat, lon, kind) in enumerate(HEROES):
        cx0 = x0 + i * (cw + 10)
        cx1 = cx0 + cw
        art_for(kind, d, cx0, y0, cx0 + 150, y0 + 152)
        num_chip(d, cx0 + 4, y0 + 4, n, size=18)
        tx = cx0 + 158
        tw = cx1 - tx
        y = y0
        for ln in wrap_n(d, head, f_head, tw, 3):
            d.text((tx, y), ln, font=f_head, fill=INK)
            y += 17
        y += 1
        for ln in wrap_n(d, deck, f_deck, tw, 3):
            d.text((tx, y), ln, font=f_deck, fill=INK_SOFT)
            y += 13
        tag(d, tx, y + 2, tagtxt)
        if i:
            d.line([(cx0 - 5, y0), (cx0 - 5, y0 + 152)], fill=RULE, width=1)
    rule(d, x0, x1, 290, fill=INK, width=2)


def draw_mids(d):
    y0 = 296
    x0, x1 = 14, W - 14
    rows = [MIDS[0:4], MIDS[4:8], MIDS[8:13]]
    f_head = font(F_SERIF_B, 12)
    f_head5 = font(F_SERIF_B, 11)
    f_deck = font(F_SANS, 9)
    f_tag = font(F_SANS_B, 8)
    f_tag5 = font(F_SANS_B, 7)
    row_h, gap = 90, 2
    for r, row in enumerate(rows):
        ry = y0 + r * (row_h + gap)
        cw = (x1 - x0 - (len(row) - 1) * 10) // len(row)
        aw = 76 if len(row) == 4 else 64
        for i, (n, head, deck, tagtxt, lat, lon, kind, region) in enumerate(row):
            cx0 = x0 + i * (cw + 10)
            cx1 = cx0 + cw
            art_for(kind, d, cx0, ry + 1, cx0 + aw, ry + 1 + 88)
            num_chip(d, cx0 + 3, ry + 4, n, size=14)
            tx = cx0 + aw + 6
            tw = cx1 - tx
            fh = f_head if len(row) == 4 else f_head5
            ft = f_tag if len(row) == 4 else f_tag5
            y = ry + 2
            for ln in wrap_n(d, head, fh, tw, 3):
                d.text((tx, y), ln, font=fh, fill=INK)
                y += 14 if len(row) == 4 else 13
            for ln in wrap_n(d, deck, f_deck, tw, 2):
                d.text((tx, y), ln, font=f_deck, fill=INK_SOFT)
                y += 11
            d.text((tx, y + 1), tagtxt, font=ft, fill=ACCENT)
            if i:
                d.line([(cx0 - 5, ry), (cx0 - 5, ry + row_h - 2)],
                       fill=RULE, width=1)
        if r < 2:
            rule(d, x0, x1, ry + row_h + 1, fill=RULE, width=1)


def draw_briefs(d):
    y0 = 576
    x0, x1 = 14, W - 14
    f_sec = font(F_SANS_B, 11)
    d.text((x0, y0), "IN BRIEF", font=f_sec, fill=ACCENT_DK)
    rule(d, x0 + 62, x1, y0 + 6, fill=RULE, width=1)
    cols = [BRIEFS[0:8], BRIEFS[8:16], BRIEFS[16:23]]
    f_head = font(F_SANS_B, 9)
    cw = (x1 - x0 - 20) // 3
    for c, col in enumerate(cols):
        cx0 = x0 + c * (cw + 10)
        y = y0 + 18
        for (n, head, deck, tagtxt, lat, lon, region) in col:
            src = tagtxt.split("—")[-1].strip()
            line = "%d. %s · %s" % (n, head, src)
            line = fit_line(d, line, f_head, cw)
            d.text((cx0, y), line, font=f_head, fill=INK)
            y += 14
        if c:
            d.line([(cx0 - 5, y0 + 18), (cx0 - 5, y0 + 18 + 8 * 14)],
                   fill=RULE, width=1)


def draw_map(d):
    mx0, my0, mx1, my1 = 14, 708, W - 14, 890
    MAP["y0"], MAP["y1"] = my0, my1
    draw_map_land(d, mx0, my0, mx1, my1)
    # graticule
    for lon in range(-150, 181, 30):
        x, _ = lonlat_to_xy(lon, 0, mx0, my0, mx1, my1)
        d.line([(x, my0), (x, my1)], fill=(180, 192, 190), width=1)
    for lat in (-30, 0, 30, 60):
        _, y = lonlat_to_xy(0, lat, mx0, my0, mx1, my1)
        d.line([(mx0, y), (mx1, y)], fill=(180, 192, 190), width=1)
    # ocean labels (centred on their anchor so none runs off the frame)
    f_ocean = font(F_SERIF, 11)
    for txt, lon, lat in (("ATLANTIC", -30, 8), ("PACIFIC", -150, -8),
                          ("PACIFIC", 165, -20), ("INDIAN", 80, -30)):
        x, y = lonlat_to_xy(lon, lat, mx0, my0, mx1, my1)
        tw = d.textlength(txt, font=f_ocean)
        d.text((x - tw / 2, y), txt, font=f_ocean, fill=(120, 140, 140))
    # dots + badges
    dots = []
    for num, lat, lon in PINS:
        x, y = lonlat_to_xy(lon, lat, mx0, my0, mx1, my1)
        dots.append((num, x, y))
    badges = solve_badges(dots)
    f_num = font(F_SANS_B, 8)
    dot_by_num = {num: (x, y) for num, x, y in dots}
    for num, bx0, by0, bx1, by1 in badges:
        dx, dy = dot_by_num[num]
        bcx, bcy = (bx0 + bx1) / 2, (by0 + by1) / 2
        d.line([(dx, dy), (bcx, bcy)], fill=(90, 82, 66), width=1)
    for num, x, y in dots:
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(250, 246, 236),
                  outline=ACCENT, width=2)
        d.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=ACCENT)
    for num, bx0, by0, bx1, by1 in badges:
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=3, fill=ACCENT)
        t = str(num)
        tw = d.textlength(t, font=f_num)
        d.text(((bx0 + bx1 - tw) / 2, by0 + 2), t, font=f_num,
               fill=(250, 246, 236))
    d.rectangle([mx0, my0, mx1, my1], outline=INK, width=2)
    f_foot = font(F_SANS, 9)
    d.text((mx0, my1 + 4),
           "ALL DOTS AT TRUE LOCATIONS  ·  5 = QUAKE AT SEA OFF VANUATU",
           font=f_foot, fill=MUTED)
    return dots, badges


def draw_datecheck(d):
    y0 = 906
    x0, x1 = 14, W - 14
    f_sec = font(F_SANS_B, 11)
    d.text((x0, y0), "DATE CHECK — NOT TODAY", font=f_sec, fill=ACCENT_DK)
    rule(d, x0 + 148, x1, y0 + 6, fill=RULE, width=1)
    f_item = font(F_SANS, 10)
    cw = (x1 - x0 - 30) // 4
    for i, item in enumerate(DATECHECK):
        cx0 = x0 + (i % 4) * (cw + 10)
        cy = y0 + 16 + (i // 4) * 14
        txt = fit_line(d, "\u2715  " + item, f_item, cw)
        d.text((cx0, cy), txt, font=f_item, fill=INK_SOFT)


def draw_regions(d):
    y0 = 950
    x0, x1 = 14, W - 14
    f_sec = font(F_SANS_B, 11)
    d.text((x0, y0), "STORIES BY REGION", font=f_sec, fill=ACCENT_DK)
    rule(d, x0 + 118, x1, y0 + 6, fill=RULE, width=1)
    total = sum(c for _, c in REGIONS)
    assert total == 39, "region bar must sum to 39, got %d" % total
    bar_y, bar_h = y0 + 16, 10
    palette = [ACCENT, (31, 58, 95), (38, 92, 50), (176, 132, 40),
               (120, 60, 120), (0, 120, 120), (180, 90, 40), (90, 110, 60)]
    bx = x0
    for i, (label, count) in enumerate(REGIONS):
        wseg = (x1 - x0) * count / total
        d.rectangle([bx, bar_y, bx + wseg, bar_y + bar_h],
                    fill=palette[i % len(palette)])
        bx += wseg
    # one centred legend line with colour dots — per-segment labels collide
    # on the narrow segments (Middle East 2, Africa 1, Oceania 2)
    f_lab = font(F_SANS_B, 9)
    parts, widths = [], []
    for i, (label, count) in enumerate(REGIONS):
        parts.append((palette[i % len(palette)], "%s %d" % (label, count)))
    gap = 14
    total_w = sum(d.textlength(t, font=f_lab) + 10 for _, t in parts)
    total_w += gap * (len(parts) - 1)
    lx = x0 + (x1 - x0 - total_w) / 2
    ly = bar_y + bar_h + 4
    for i, (col, txt) in enumerate(parts):
        d.ellipse([lx, ly + 1, lx + 7, ly + 8], fill=col)
        d.text((lx + 10, ly), txt, font=f_lab, fill=INK_SOFT)
        lx += d.textlength(txt, font=f_lab) + 10 + gap


def draw_footer(d):
    f = font(F_SANS, 9)
    draw_centered(d, W // 2, 998,
                  "Compiled from AP, Reuters, BBC, AFP, The Hindu, USGS, "
                  "PHIVOLCS, Oxfam and others  ·  All stories dated Monday "
                  "23 November 2026  ·  The World in One Page",
                  f, MUTED)


def render():
    global _IMG
    img = make_paper()
    _IMG = img
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_stats(d)
    draw_heroes(d)
    draw_mids(d)
    draw_briefs(d)
    dots, badges = draw_map(d)
    draw_datecheck(d)
    draw_regions(d)
    draw_footer(d)
    return img, dots, badges


def main():
    img, dots, badges = render()
    img.save(OUT, format="PNG", optimize=True)
    print("saved", OUT)
    return img, dots, badges


if __name__ == "__main__":
    main()
