#!/usr/bin/env python3
"""THE WORLD TODAY — Monday 23 November 2026 in one image.
Fresh build for make.fun news-image-20261123 (v3). Draws a dense serif
newspaper front page: 3 heroes + 13 illustrated mids + 23 briefs,
numbered map, DATE CHECK box. Deterministic, PIL only.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 24                      # outer margin
CW = 976                    # content width (24..1000)

PAPER = (247, 241, 227)     # warm newsprint
PAPER_DK = (238, 230, 212)
INK = (26, 26, 26)
INK_SOFT = (74, 74, 74)
RED = (178, 32, 44)
RED_DK = (140, 20, 32)
GOLD = (176, 141, 60)
LAND_FILL = (224, 212, 182)
LAND_EDGE = (120, 104, 74)
SEA = (214, 226, 228)
CARD_BG = (252, 249, 240)
CARD_EDGE = (190, 178, 150)
TAG_BG = (26, 26, 26)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap, returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- data
# (num, headline, deck, tag, source, lon, lat, region, art)
# lon/lat None = global story, no map dot (footnoted).
HEROES = [
    (1, "MERKURY SUNK OFF LIBYA",
     "Zelenskyy says seven Ukrainian sea drones sank the Russian "
     "warship Merkury off Benghazi and downed a Ka-27 helicopter.",
     "CONFIRMED", "REUTERS", 20.07, 32.10, "Europe", "ship"),
    (2, "US HITS IRAN SHADOW BANKS",
     "Treasury sanctions two dozen exchange houses and front firms "
     "in a $14.7bn Iranian shadow-banking network.",
     "CONFIRMED", "US TREASURY", -77.04, 38.90, "North America", "bank"),
    (3, "TAIEX REBOUNDS 779 POINTS",
     "Taiwan stocks swing 1,666 points in a day as a short-selling "
     "ban takes effect and the stabilisation fund steps in.",
     "CONFIRMED", "FOCUS TAIWAN", 121.56, 25.03, "East Asia", "chart"),
]

MIDS = [
    (4, "NATO MEETS ON POLAND STRIKES",
     "Allies meet in Brussels after three Kh-101s hit Poland; Warsaw "
     "seeks air defence.",
     "CONFIRMED", "NATO", 4.35, 50.85, "Europe", "nato"),
    (5, "KYIV STRIKES KILL 15",
     "Russian bombardment kills at least 15 around Kyiv; a boy is "
     "pulled alive from the rubble.",
     "CONFIRMED", "KYIV OFFICIALS", 30.52, 50.45, "Europe", "blast"),
    (6, "ODESA SCHOOLS GO REMOTE",
     "Odesa schools go remote to 27 Nov; grid wrecked, 135,000 "
     "without power.",
     "REPORTED", "FRANCE 24", 30.72, 46.48, "Europe", "school"),
    (7, "GAZA 'TOXIC WASTELAND'",
     "Oxfam says Gaza is now a toxic wasteland; 99% of its water is "
     "contaminated.",
     "REPORTED", "OXFAM", 34.47, 31.50, "Middle East", "rubble"),
    (8, "CHAPO ISIDRO EXTRADITION",
     "US seeks extradition of the FBI most-wanted drug lord seized "
     "Friday; 21 were killed.",
     "CONFIRMED", "REUTERS", -108.47, 25.57, "North America", "cartel"),
    (9, "BITCOIN BACK ABOVE $61K",
     "Bitcoin back above $61,000 after a weekend plunge to $55,130, "
     "its lowest since Sept 2024.",
     "CONFIRMED", "COINDESK", None, None, "Global", "coin"),
    (10, "KOSPI PLUNGES, SIDECAR TRIPS",
     "Kospi dives more than 5% intraday, tripping a five-minute "
     "sell-side sidecar; it closes 3.3% down at 4,709.",
     "CONFIRMED", "YONHAP", 126.98, 37.57, "East Asia", "fall"),
    (11, "UN CHIEF URGES AI RULES",
     "Guterres calls for a global AI safety framework within a year "
     "at the Bridgetown summit; a $3bn fund is proposed.",
     "CONFIRMED", "UN NEWS", -59.60, 13.18, "North America", "summit"),
    (12, "NUCLEAR SATELLITE ALARM",
     "Three German outlets report Moscow is set to launch a "
     "nuclear-armed satellite.",
     "REPORTED", "NDR / WDR", 37.62, 55.76, "Europe", "satellite"),
    (13, "CIKANDE FIRE TOLL 24",
     "Sweets-factory fire in Banten kills at least 24, with about "
     "30 missing; the search goes on.",
     "REPORTED", "REUTERS", 106.15, -6.12, "Southeast Asia", "fire"),
    (14, "SK HYNIX ADRs JUMP 20%",
     "US-listed SK Hynix shares jump 20% to $124 as Nvidia "
     "reinstates Jensen Huang; Seoul shares fell 2.5%.",
     "CONFIRMED", "ASIA DAILY", 126.98, 37.57, "East Asia", "fund"),
    (15, "NHS TRIALS AI SCREENING",
     "NHS starts a trial of AI in breast-cancer screening for "
     "700,000 women to catch tumours earlier.",
     "CONFIRMED", "NHS", -0.13, 51.50, "Europe", "hospital"),
    (16, "SEOUL READIES RESCUE FUND",
     "Korea prepares a 10.76-trillion-won market stabilisation fund, "
     "unused since 2008, as stocks slide.",
     "REPORTED", "SEOUL", 126.98, 37.57, "East Asia", "fund"),
]

BRIEFS = [
    (17, "EU UNVEILS 22ND SANCTIONS",
     "Von der Leyen's package covers banks, crypto and sport.",
     4.35, 50.85, "Europe"),
    (18, "NVIDIA SOARS 31% AS HUANG RETURNS",
     "Huang returns as Nvidia CEO; shares jump 31% to $165.",
     -121.95, 37.35, "North America"),
    (19, "BRAZIL EYES 2% SURPLUS",
     "Brazil targets a 1.5–2% primary surplus; growth cut to 1.8%.",
     -46.63, -23.55, "South America"),
    (20, "NASDAQ FUTURES UP 3%",
     "Wall Street set to bounce after Friday's correction.",
     -73.99, 40.73, "North America"),
    (21, "TRUMP CURBS CONGRESS PROBES",
     "Congress must show a valid legislative purpose to seek files.",
     -77.04, 38.90, "North America"),
    (22, "ISTANBUL RALLIES",
     "Thousands protest the crackdown on opposition and media.",
     28.98, 41.01, "Europe"),
    (23, "EURO INFLATION 4.0%",
     "Eurostat figures show prices rising again.",
     8.68, 50.11, "Europe"),
    (24, "MODI HOSTS NEPAL PM",
     "India pledges a $1.63bn fund and an IIT campus in Nepal.",
     77.21, 28.61, "South Asia"),
    (25, "CÚCUTA DRONE ATTACK",
     "Three hurt, including an infant; 60 homes damaged.",
     -72.51, 7.89, "South America"),
    (26, "FINLAND BACKS BORDER BARRIERS",
     "Parliament backs anti-tank barriers on the Russia border.",
     24.94, 60.17, "Europe"),
    (27, "DEMOCRATS SET 2028 PRIMARY",
     "Democrats unveil the 2028 primary calendar after midterm wins.",
     -77.04, 38.90, "North America"),
    (28, "GOMEZ TO RESIGN",
     "Congressman quits 1 Dec after ethics report.",
     -118.24, 34.05, "North America"),
    (29, "SA COUNCILS STALL IN TALKS",
     "Johannesburg sitting postponed; 14 councils told to delay.",
     28.05, -26.20, "Africa"),
    (30, "ICE ARRESTS AT SEATTLE AIRPORT",
     "Agents detain travellers in 'horrific' scene, witnesses say.",
     -122.33, 47.61, "North America"),
    (31, "DHAKA WAGE TALKS",
     "Garment makers eye a 15% rise, far short of demands.",
     90.41, 23.81, "South Asia"),
    (32, "NIGERIA VILLA BLACKOUT",
     "Presidential villa hit by water and power cuts.",
     7.49, 9.06, "Africa"),
    (33, "BAYELSA BOAT SEARCH",
     "Rescuers race on after a funeral boat capsizes; 24 dead.",
     6.33, 4.93, "Africa"),
    (34, "UNRWA STAFFER KILLED",
     "One dead, three hurt in an Israeli strike on Gaza.",
     34.47, 31.50, "Middle East"),
    (35, "HOUTHI STRIKES TAIZ",
     "Two killed, eight hurt in attacks on the Yemeni city.",
     44.01, 13.58, "Middle East"),
    (36, "CHINA CUTS MARGIN TO 80%",
     "China cuts the margin ratio for leveraged buys to 80% from 100%.",
     121.47, 31.23, "East Asia"),
    (37, "MERZ WARNS RUSSIA OFF",
     "Merz tells Russia to halt provocations; 3 missiles hit Poland.",
     13.41, 52.52, "Europe"),
    (38, "LIBYA PARLIAMENT UNITY PUSH",
     "Parliament launches a push to unify government and hold elections.",
     13.19, 32.90, "Africa"),
    (39, "CHINA IN AI TALKS PACT",
     "Beijing agrees a new AI discussion mechanism.",
     116.41, 39.90, "East Asia"),
]

DATE_CHECK = [
    ("Sparta II cargo-ship fire", "Sat 21 Nov"),
    ("BepiColombo enters Mercury orbit", "Sun 22 Nov"),
    ("Shuri Castle restoration ceremony", "Sun 22 Nov"),
    ("Barcelona 3-2 comeback at Villarreal", "Sun 22 Nov"),
    ("Verstappen wins Las Vegas GP", "Sat 21 Nov"),
    ("FBI crime database hacked", "Sat 21 Nov"),
    ("Belgrade record 12-hour rain", "19–20 Nov"),
    ("Shizuoka 5.7 quake, 22 hurt", "8 Nov"),
    ("COP31 ends with no deal", "Sun 22 Nov"),
    ("Alcaraz wins ATP Finals", "Sun 22 Nov"),
    ("AI 'proves' Riemann", "Fri 20 Nov"),
    ("Skubal's $450m Mets deal", "Sun 22 Nov"),
]

STATS = [
    ("+778.6", "TAIEX POINTS GAINED"),
    ("24+", "IRAN TARGETS SANCTIONED"),
    ("5%", "KOSPI INTRADAY PLUNGE"),
    ("24", "DEAD IN CIKANDE FIRE"),
]

ALL_STORIES = HEROES + MIDS + [(n, h, d, None, None, lo, la, r, None)
                                for (n, h, d, lo, la, r) in BRIEFS]

REGIONS = ["Europe", "North America", "East Asia", "Middle East",
           "South Asia", "Africa", "Southeast Asia", "South America",
           "Oceania", "Global"]
REGION_COLORS = {
    "Europe": (178, 32, 44), "North America": (38, 84, 138),
    "East Asia": (176, 141, 60), "Middle East": (110, 84, 140),
    "South Asia": (42, 122, 90), "Africa": (196, 110, 40),
    "Southeast Asia": (66, 140, 150), "South America": (150, 90, 60),
    "Oceania": (90, 120, 80), "Global": (120, 120, 120),
}

# ---------------------------------------------------------------- map data
# Coarse continent outlines (lon, lat), drawn from general geography.
# Verified programmatically: every story pin must fall on land (except
# footnoted sea/global stories).
LAND = [
    # North America (incl. Central America)
    [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 58),
     (-130, 54), (-125, 49), (-124, 42), (-123, 38), (-120, 34), (-114, 29), (-110, 24),
     (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
     (-80, 8), (-77, 7), (-79, 9), (-82, 10), (-84, 13), (-87, 16),
     (-90, 18), (-91, 19), (-96, 19), (-97, 22), (-97, 26), (-93, 30),
     (-89, 30), (-84, 30), (-81, 26), (-80, 32), (-76, 35), (-74, 40),
     (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-65, 50), (-60, 52),
     (-64, 58), (-68, 55), (-72, 58), (-78, 62), (-85, 66), (-92, 66),
     (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68)],
    # Greenland
    [(-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68), (-22, 70),
     (-20, 74), (-25, 78), (-35, 80), (-50, 80), (-58, 76), (-62, 72)],
    # South America
    [(-79, 9), (-77, 4), (-78, -2), (-81, -4), (-81, -6), (-77, -12),
     (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
     (-70, -54), (-66, -55), (-68, -50), (-65, -45), (-62, -41), (-58, -35),
     (-52, -33), (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6),
     (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9),
     (-68, 11), (-72, 12), (-75, 10)],
    # Africa
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-6, 35), (0, 36),
     (10, 37), (11, 34), (19, 33), (20, 32), (25, 32), (30, 31), (32, 31),
     (34, 28), (35, 24), (37, 20), (39, 15), (43, 11), (48, 11), (51, 10),
     (51, 2), (46, -2), (41, -4), (40, -10), (36, -18), (33, -26),
     (28, -33), (20, -35), (17, -32), (15, -27), (13, -18), (12, -12),
     (13, -6), (9, -1), (9, 4), (-8, 4), (-13, 8)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -20)],
    # Eurasia (mainland; Baltic/Med/Black/Caspian drawn back as sea below)
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50),
     (0, 51), (3, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62),
     (12, 65), (18, 69), (25, 71), (30, 70), (32, 68), (40, 68), (45, 68),
     (50, 69), (55, 68), (60, 69), (68, 70), (75, 72), (80, 73), (90, 75),
     (100, 76), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (158, 69), (162, 66), (170, 66), (178, 65), (178, 62), (170, 60),
     (162, 58), (158, 52), (156, 50), (150, 59), (142, 59), (142, 54),
     (140, 46), (135, 43), (132, 43), (129, 35), (126.5, 34.8),
     (124.5, 39.5), (121, 39), (119, 35), (122, 31.8), (121, 30), (120, 28), (115, 23), (110, 20), (108, 18),
     (105, 10), (103, 8), (100, 7), (98, 10), (97, 15), (94, 17), (92, 21),
     (89, 22), (86, 20), (83, 18), (80, 15), (77, 8), (75, 10), (72, 20),
     (70, 23), (66, 25), (62, 25), (58, 26), (56, 27), (54, 26), (52, 25),
     (50, 29), (48, 30), (44, 30), (40, 31), (36, 31), (34, 31), (33, 36),
     (30, 36), (27, 37), (23, 36), (22, 37), (19, 40), (23, 40), (26, 40),
     (28, 41), (26, 41), (23, 40), (19, 42), (15, 44), (12, 44), (8, 44),
     (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37)],
    # Arabia + Levant
    [(34.0, 31.2), (35.5, 33), (36, 36), (39, 32), (42, 29), (41, 24),
     (40, 20), (42.5, 15), (43, 12.8), (46, 13.8), (48, 15), (51, 12.8),
     (55, 17), (58, 21), (59, 24), (56, 26), (52, 26), (49, 29), (46, 30),
     (42, 30), (38, 30), (35, 31)],
    # United Kingdom
    [(-5.7, 50.0), (-3.5, 50.7), (-1.8, 50.8), (1.3, 51.1), (1.8, 52.6),
     (0.5, 52.9), (-0.5, 53.5), (-2.5, 55.0), (-3.0, 56.0), (-5.0, 56.5),
     (-5.7, 55.0), (-4.5, 53.0), (-5.3, 51.8)],
    # Japan
    [(130, 31), (131, 33), (133, 34), (135, 34), (137, 35), (139, 35),
     (140, 37), (141, 39), (141, 41), (142, 43), (144, 44), (143, 42),
     (141, 39), (140, 36), (138, 35), (135, 33), (132, 33), (130, 31)],
    # Taiwan
    [(120.1, 22.6), (120.3, 23.5), (121.0, 25.3), (121.9, 25.3),
     (121.9, 24.5), (121.0, 22.8)],
    # Sumatra
    [(95.3, 5.6), (97.5, 5.2), (100, 0), (102, -2), (104, -4), (106, -6),
     (104.5, -5.5), (102, -3), (99.5, 1), (97, 4), (95.3, 5.6)],
    # Java
    [(105.2, -6.5), (106.5, -5.9), (108, -6.5), (110, -6.8), (112, -6.9),
     (114, -7.5), (114.5, -8.6), (112, -8.2), (110, -7.8), (108, -7.7),
     (106, -7.6), (105.2, -6.5)],
    # Borneo
    [(109, 1.5), (111, 3), (113, 4.5), (116, 6), (118, 4), (117, 1),
     (116, -2), (114, -4), (111, -3.5), (109, -1), (109, 1.5)],
    # Sulawesi
    [(119, 0), (120.5, 1), (123, 0.5), (121, -1), (120, -3), (119.5, -5),
     (119, -3), (119, 0)],
    # New Guinea
    [(131, -1), (134, -2), (137, -3), (140, -4), (143, -6), (146, -8),
     (150, -10), (147, -9), (144, -8), (141, -8), (138, -7), (135, -4),
     (132, -2), (131, -1)],
    # Philippines (Luzon + Mindanao blob)
    [(120, 18.5), (121.5, 18), (122, 16), (121, 14), (122, 11), (124, 10),
     (126, 7), (124, 6), (122, 7), (120.5, 10), (119.5, 13), (120, 16),
     (120, 18.5)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38.6), (145, -38.6),
     (147, -39), (150, -37), (153, -32), (153, -27), (150, -23), (146, -19),
     (142, -15), (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
    # New Zealand
    [(167, -45), (168, -44), (170, -42), (173, -41), (175, -38), (177, -38),
     (175, -40), (172, -43), (168, -46), (167, -45)],
    # Sri Lanka
    [(79.8, 9.8), (80.8, 9.5), (81.8, 8.5), (81.5, 6.5), (80.5, 5.9),
     (79.8, 7.5), (79.8, 9.8)],
    # Barbados
    [(-59.70, 13.35), (-59.50, 13.35), (-59.45, 13.15), (-59.55, 13.05),
     (-59.70, 13.10)],
]

# Inland seas / gulfs drawn back in sea colour over the land fill.
SEA_INSETS = [
    # Mediterranean
    [(-6, 36), (0, 36), (3, 37), (10, 37), (11, 34), (19, 33), (20, 32),
     (25, 32), (30, 31), (32, 31), (34, 31), (36, 36), (30, 36), (27, 37),
     (23, 36), (22, 37), (19, 40), (15, 40), (12, 38), (8, 39), (3, 38),
     (0, 38), (-2, 37), (-6, 36)],
    # Black Sea
    [(28, 41), (30, 41.5), (33, 41.5), (36, 41), (39, 41), (41, 41.5),
     (41, 44), (39, 46), (36, 46), (33, 46), (31, 46.5), (29, 45.5),
     (28, 43), (28, 41)],
    # Caspian Sea
    [(47, 37), (50, 37), (52, 39), (53, 42), (52, 45), (50, 47), (47, 47),
     (46, 44), (46, 40), (47, 37)],
    # Baltic Sea
    [(10, 54), (13, 54), (18, 55), (21, 56), (24, 58), (24, 60), (21, 62),
     (18, 63), (15, 60), (12, 57), (10, 55), (10, 54)],
    # Red Sea
    [(35, 29), (37, 27), (39, 24), (40, 21), (41, 18), (43, 14), (43, 12.5),
     (41, 15), (39, 20), (37, 24), (35, 28), (35, 29)],
    # Persian Gulf
    [(48, 30), (50, 29), (52, 27), (54, 26), (56, 26), (57, 25), (54, 27),
     (51, 28), (49, 29), (48, 30)],
    # Hudson Bay
    [(-85, 55), (-80, 55), (-77, 58), (-78, 62), (-82, 63), (-86, 60),
     (-88, 57), (-85, 55)],
]


def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)):
            xint = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xint:
                inside = not inside
        j = i
    return inside


def on_land(lon, lat):
    return any(point_in_poly(lon, lat, p) for p in LAND)


# ---------------------------------------------------------------- art
def art(draw, kind, x0, y0, x1, y1):
    """Simple flat vector illustration inside (x0,y0)-(x1,y1)."""
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sky = {"ship": (168, 200, 214), "summit": (196, 214, 190),
           "chart": (232, 222, 190), "nato": (200, 208, 220),
           "blast": (226, 196, 170), "school": (214, 226, 200),
           "rubble": (210, 196, 176), "cartel": (206, 204, 196),
           "tennis": (196, 214, 170), "bank": (220, 212, 180),
           "math": (210, 206, 226), "satellite": (52, 58, 84),
           "fire": (232, 190, 150), "baseball": (210, 226, 200),
           "hospital": (226, 228, 232), "fund": (222, 214, 180),
           "coin": (240, 220, 160), "fall": (238, 214, 196)}[kind]
    draw.rectangle([x0, y0, x1, y1], fill=sky)
    if kind == "ship":
        draw.rectangle([x0, y0 + h * 0.62, x1, y1], fill=(58, 96, 128))
        draw.polygon([(x0 + w * 0.15, y0 + h * 0.62), (x0 + w * 0.85, y0 + h * 0.62),
                      (x0 + w * 0.78, y0 + h * 0.42), (x0 + w * 0.22, y0 + h * 0.42)],
                     fill=(90, 60, 48))
        draw.rectangle([x0 + w * 0.42, y0 + h * 0.18, x0 + w * 0.50, y0 + h * 0.44],
                       fill=(120, 90, 70))
        draw.ellipse([x0 + w * 0.68, y0 + h * 0.10, x0 + w * 0.80, y0 + h * 0.24],
                     fill=(240, 200, 90))
        for k in range(3):
            draw.arc([x0 + w * (0.15 + 0.22 * k), y0 + h * 0.70,
                      x0 + w * (0.35 + 0.22 * k), y0 + h * 0.86],
                     180, 360, fill=(240, 244, 246), width=2)
    elif kind == "summit":
        draw.ellipse([cx - w * 0.26, cy - h * 0.30, cx + w * 0.26, cy + h * 0.30],
                     outline=(52, 96, 110), width=3)
        draw.ellipse([cx - w * 0.26, cy - h * 0.30, cx + w * 0.26, cy + h * 0.30],
                     fill=(120, 160, 190))
        draw.arc([cx - w * 0.26, cy - h * 0.12, cx + w * 0.26, cy + h * 0.12],
                 200, 340, fill=(240, 244, 246), width=2)
        draw.line([x0 + w * 0.10, y0 + h * 0.82, x1 - w * 0.10, y0 + h * 0.82],
                  fill=(90, 90, 90), width=2)
        for k, c in enumerate([(178, 32, 44), (38, 84, 138), (42, 122, 90)]):
            fx = x0 + w * (0.22 + 0.28 * k)
            draw.line([fx, y0 + h * 0.82, fx, y0 + h * 0.52], fill=INK, width=2)
            draw.polygon([(fx, y0 + h * 0.52), (fx + w * 0.16, y0 + h * 0.58),
                          (fx, y0 + h * 0.64)], fill=c)
    elif kind == "chart":
        pts = [(x0 + w * 0.08, y0 + h * 0.55), (x0 + w * 0.28, y0 + h * 0.62),
               (x0 + w * 0.45, y0 + h * 0.45), (x0 + w * 0.62, y0 + h * 0.58),
               (x0 + w * 0.80, y0 + h * 0.28), (x0 + w * 0.94, y0 + h * 0.20)]
        draw.line(pts, fill=(178, 32, 44), width=3)
        for p in pts:
            draw.ellipse([p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2], fill=RED)
        draw.line([x0 + w * 0.08, y0 + h * 0.85, x1 - w * 0.06, y0 + h * 0.85],
                  fill=INK, width=2)
    elif kind == "nato":
        draw.rectangle([x0 + w * 0.14, y0 + h * 0.30, x1 - w * 0.14, y1 - 2],
                       fill=(200, 204, 212))
        for k in range(4):
            draw.rectangle([x0 + w * (0.20 + 0.16 * k), y0 + h * 0.42,
                            x0 + w * (0.28 + 0.16 * k), y0 + h * 0.58],
                           fill=(90, 110, 140))
        draw.polygon([(x0 + w * 0.10, y0 + h * 0.32), (cx, y0 + h * 0.10),
                      (x1 - w * 0.10, y0 + h * 0.32)], fill=(120, 90, 60))
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(240, 200, 90))
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=(240, 200, 90), width=2)
    elif kind == "blast":
        for k, r in enumerate([0.42, 0.30, 0.18]):
            draw.ellipse([cx - w * r, cy - h * r, cx + w * r, cy + h * r],
                         fill=[(240, 170, 60), (232, 110, 50), (250, 220, 120)][k])
        for k in range(8):
            a = math.pi * k / 4
            draw.line([cx + math.cos(a) * w * 0.30, cy + math.sin(a) * h * 0.30,
                       cx + math.cos(a) * w * 0.48, cy + math.sin(a) * h * 0.48],
                      fill=(120, 60, 40), width=2)
    elif kind == "school":
        draw.rectangle([x0 + w * 0.16, y0 + h * 0.38, x1 - w * 0.16, y0 + h * 0.88],
                       fill=(190, 160, 120))
        draw.polygon([(x0 + w * 0.10, y0 + h * 0.40), (cx, y0 + h * 0.16),
                      (x1 - w * 0.10, y0 + h * 0.40)], fill=(140, 50, 50))
        draw.rectangle([cx - w * 0.07, y0 + h * 0.62, cx + w * 0.07, y0 + h * 0.88],
                       fill=(70, 50, 40))
        draw.rectangle([x0 + w * 0.24, y0 + h * 0.48, x0 + w * 0.34, y0 + h * 0.58],
                       fill=(40, 40, 50))
        draw.rectangle([x1 - w * 0.34, y0 + h * 0.48, x1 - w * 0.24, y0 + h * 0.58],
                       fill=(240, 220, 140))
        draw.line([x1 - w * 0.12, y0 + h * 0.88, x1 - w * 0.12, y0 + h * 0.20],
                  fill=INK, width=2)
        draw.polygon([(x1 - w * 0.12, y0 + h * 0.20), (x1 - w * 0.02, y0 + h * 0.26),
                      (x1 - w * 0.12, y0 + h * 0.32)], fill=RED)
    elif kind == "rubble":
        for k, (px, py, pw, ph) in enumerate([(0.12, 0.62, 0.30, 0.26),
                                             (0.38, 0.55, 0.26, 0.33),
                                             (0.62, 0.66, 0.26, 0.22)]):
            draw.polygon([(x0 + w * px, y0 + h * (py + ph)),
                          (x0 + w * (px + pw / 2), y0 + h * py),
                          (x0 + w * (px + pw), y0 + h * (py + ph))],
                         fill=(150, 130, 110))
        draw.line([x0 + w * 0.30, y0 + h * 0.30, x0 + w * 0.55, y0 + h * 0.55],
                  fill=(120, 110, 100), width=2)
        draw.line([x0 + w * 0.60, y0 + h * 0.25, x0 + w * 0.45, y0 + h * 0.50],
                  fill=(120, 110, 100), width=2)
    elif kind == "cartel":
        draw.ellipse([x0 + w * 0.14, cy - h * 0.22, x0 + w * 0.38, cy + h * 0.22],
                     outline=INK, width=3)
        draw.ellipse([x1 - w * 0.38, cy - h * 0.22, x1 - w * 0.14, cy + h * 0.22],
                     outline=INK, width=3)
        draw.line([x0 + w * 0.38, cy, x1 - w * 0.38, cy], fill=INK, width=3)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    elif kind == "tennis":
        draw.ellipse([cx - w * 0.30, cy - h * 0.30, cx + w * 0.30, cy + h * 0.30],
                     fill=(200, 230, 90), outline=(255, 255, 255), width=2)
        draw.arc([cx - w * 0.30, cy - h * 0.30, cx + w * 0.30, cy + h * 0.30],
                 300, 60, fill=(255, 255, 255), width=2)
        draw.arc([cx - w * 0.30, cy - h * 0.30, cx + w * 0.30, cy + h * 0.30],
                 120, 240, fill=(255, 255, 255), width=2)
        draw.line([x0 + w * 0.10, y0 + h * 0.86, x1 - w * 0.10, y0 + h * 0.86],
                  fill=(90, 140, 60), width=3)
    elif kind == "bank":
        draw.rectangle([x0 + w * 0.16, y0 + h * 0.30, x1 - w * 0.16, y0 + h * 0.38],
                       fill=(120, 110, 80))
        for k in range(4):
            draw.rectangle([x0 + w * (0.20 + 0.16 * k), y0 + h * 0.42,
                            x0 + w * (0.28 + 0.16 * k), y0 + h * 0.78],
                           fill=(150, 140, 105))
        draw.rectangle([x0 + w * 0.12, y0 + h * 0.80, x1 - w * 0.12, y0 + h * 0.88],
                       fill=(120, 110, 80))
        draw.ellipse([cx - w * 0.13, y0 + h * 0.10, cx + w * 0.13, y0 + h * 0.26],
                     fill=(240, 200, 90))
        draw.text((cx - 3, y0 + h * 0.11), "$", font=font(F_SANS_B, 11), fill=INK)
    elif kind == "math":
        draw.text((cx - w * 0.22, cy - h * 0.32), "π", font=font(F_SERIF_B, 30),
                  fill=(52, 52, 120))
        draw.text((cx + w * 0.05, cy - h * 0.05), "ζ(s) = 0",
                  font=font(F_SERIF, 11), fill=INK)
        draw.line([x0 + w * 0.12, y0 + h * 0.80, x1 - w * 0.12, y0 + h * 0.80],
                  fill=INK, width=2)
    elif kind == "satellite":
        draw.rectangle([x0 + w * 0.30, y0 + h * 0.40, x0 + w * 0.52, y0 + h * 0.60],
                       fill=(180, 190, 205))
        draw.rectangle([x0 + w * 0.08, y0 + h * 0.44, x0 + w * 0.28, y0 + h * 0.56],
                       fill=(70, 90, 160))
        draw.rectangle([x0 + w * 0.54, y0 + h * 0.44, x0 + w * 0.74, y0 + h * 0.56],
                       fill=(70, 90, 160))
        draw.ellipse([x0 + w * 0.78, y0 + h * 0.18, x0 + w * 0.88, y0 + h * 0.30],
                     fill=(240, 200, 90))
        for k in range(6):
            x = x0 + w * (0.10 + 0.13 * k)
            y = y0 + h * (0.78 + 0.04 * ((k % 2) * 2 - 1))
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255))
    elif kind == "fire":
        draw.polygon([(cx, y0 + h * 0.08), (x0 + w * 0.72, y0 + h * 0.55),
                      (x0 + w * 0.58, y0 + h * 0.62), (x0 + w * 0.70, y0 + h * 0.85),
                      (x0 + w * 0.30, y0 + h * 0.85), (x0 + w * 0.42, y0 + h * 0.62),
                      (x0 + w * 0.28, y0 + h * 0.55)], fill=(232, 110, 40))
        draw.polygon([(cx, y0 + h * 0.42), (x0 + w * 0.62, y0 + h * 0.72),
                      (x0 + w * 0.38, y0 + h * 0.85), (x0 + w * 0.62, y0 + h * 0.72)],
                     fill=(250, 200, 80))
        draw.rectangle([x0 + w * 0.14, y0 + h * 0.86, x1 - w * 0.14, y0 + h * 0.92],
                       fill=(90, 70, 55))
    elif kind == "baseball":
        draw.ellipse([cx - w * 0.28, cy - h * 0.28, cx + w * 0.28, cy + h * 0.28],
                     fill=(250, 250, 246), outline=(200, 200, 190), width=2)
        draw.arc([cx - w * 0.28, cy - h * 0.28, cx + w * 0.28, cy + h * 0.28],
                 300, 60, fill=RED, width=2)
        draw.arc([cx - w * 0.28, cy - h * 0.28, cx + w * 0.28, cy + h * 0.28],
                 120, 240, fill=RED, width=2)
        draw.rectangle([x0 + w * 0.10, y0 + h * 0.70, x1 - w * 0.10, y0 + h * 0.80],
                       fill=(150, 90, 50))
    elif kind == "hospital":
        draw.rectangle([x0 + w * 0.18, y0 + h * 0.30, x1 - w * 0.18, y0 + h * 0.88],
                       fill=(240, 244, 246))
        draw.rectangle([cx - w * 0.10, y0 + h * 0.38, cx + w * 0.10, y0 + h * 0.72],
                       fill=RED)
        draw.rectangle([cx - w * 0.18, y0 + h * 0.48, cx + w * 0.18, y0 + h * 0.62],
                       fill=RED)
        draw.rectangle([x0 + w * 0.26, y0 + h * 0.78, x0 + w * 0.34, y0 + h * 0.86],
                       fill=(120, 160, 190))
        draw.rectangle([x1 - w * 0.34, y0 + h * 0.78, x1 - w * 0.26, y0 + h * 0.86],
                       fill=(120, 160, 190))
    elif kind == "fund":
        for k in range(5):
            bh = h * (0.25 + 0.12 * k)
            draw.rectangle([x0 + w * (0.14 + 0.17 * k), y0 + h * 0.85 - bh,
                            x0 + w * (0.26 + 0.17 * k), y0 + h * 0.85],
                           fill=(52, 110, 80) if k < 4 else (178, 32, 44))
        draw.line([x0 + w * 0.10, y0 + h * 0.85, x1 - w * 0.10, y0 + h * 0.85],
                  fill=INK, width=2)
        draw.line([x0 + w * 0.10, y0 + h * 0.55, x1 - w * 0.10, y0 + h * 0.30],
                  fill=(176, 141, 60), width=2)
    elif kind == "coin":
        draw.ellipse([cx - w * 0.30, cy - h * 0.34, cx + w * 0.30, cy + h * 0.34],
                     fill=(240, 200, 90), outline=(150, 110, 30), width=3)
        f_b = font(F_SERIF_B, 18)
        t = "B"
        tw = draw.textlength(t, font=f_b)
        draw.text((cx - tw / 2, cy - 9), t, font=f_b, fill=(120, 85, 20))
        draw.line([cx - w * 0.16, y0 + h * 0.80, cx + w * 0.16, y0 + h * 0.80],
                  fill=(150, 110, 30), width=2)
    elif kind == "fall":
        pts = [(x0 + w * 0.08, y0 + h * 0.22), (x0 + w * 0.28, y0 + h * 0.30),
               (x0 + w * 0.45, y0 + h * 0.48), (x0 + w * 0.62, y0 + h * 0.44),
               (x0 + w * 0.80, y0 + h * 0.68), (x0 + w * 0.94, y0 + h * 0.78)]
        draw.line(pts, fill=(178, 32, 44), width=3)
        for p in pts:
            draw.ellipse([p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2], fill=RED)
        draw.line([x0 + w * 0.08, y0 + h * 0.85, x1 - w * 0.06, y0 + h * 0.85],
                  fill=INK, width=2)

# ---------------------------------------------------------------- layout
def draw_card(draw, x0, y0, x1, y1, num, headline, deck, tag, source,
              art_kind, hl_size, deck_size, tag_size, art_h):
    draw.rectangle([x0, y0, x1, y1], fill=CARD_BG, outline=CARD_EDGE, width=1)
    if art_kind:
        art(draw, art_kind, x0 + 1, y0 + 1, x1 - 1, y0 + art_h)
        ty = y0 + art_h + 4
    else:
        ty = y0 + 4
    f_hl = font(F_SERIF_B, hl_size)
    f_dk = font(F_SERIF, deck_size)
    f_tg = font(F_SANS_B, tag_size)
    num_w = draw.textlength(str(num) + "  ", font=f_hl)
    # every headline line is drawn at the badge indent (x0+6+num_w),
    # so ALL lines wrap to the narrow width — wrapping the
    # continuations to the full width let them run past the card edge
    lines = wrap(draw, headline, f_hl, x1 - x0 - 10 - num_w)
    # number badge inline at start of headline
    y = ty
    draw.rectangle([x0 + 4, y + 1, x0 + 4 + num_w + 2, y + hl_size + 2],
                   fill=RED)
    draw.text((x0 + 5, y + 1), str(num), font=f_hl, fill=(255, 255, 255))
    y = text_block(draw, x0 + 6 + num_w, y, lines, f_hl, INK, hl_size + 2)
    y += 1
    dlines = wrap(draw, deck, f_dk, x1 - x0 - 10)
    y = text_block(draw, x0 + 5, y, dlines, f_dk, INK_SOFT, deck_size + 2)
    if tag:
        assert y <= y1 - tag_size - 6, \
            "card %d deck overflows into tag" % num
        tg = "%s — %s" % (tag, source)
        tw = draw.textlength(tg, font=f_tg)
        draw.rectangle([x0 + 5, y1 - tag_size - 5, x0 + 5 + tw + 6,
                        y1 - 3], fill=TAG_BG)
        draw.text((x0 + 8, y1 - tag_size - 4), tg, font=f_tg,
                  fill=(255, 255, 255))
    return y


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.line([M, 18, W - M, 18], fill=INK, width=2)
    f_title = font(F_SERIF_B, 46)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 24), title, font=f_title, fill=INK)
    f_date = font(F_SANS_B, 13)
    n_regions = len({s[7] for s in ALL_STORIES})
    date_line = ("MONDAY 23 NOVEMBER 2026  ·  39 STORIES  ·  %d REGIONS  ·  "
                 "ONE PAGE" % n_regions)
    dw = d.textlength(date_line, font=f_date)
    d.text(((W - dw) / 2, 78), date_line, font=f_date, fill=RED_DK)
    d.line([M, 98, W - M, 98], fill=INK, width=2)
    d.line([M, 101, W - M, 101], fill=INK, width=1)

    # ---- region bar
    counts = {}
    for s in ALL_STORIES:
        counts[s[7]] = counts.get(s[7], 0) + 1
    bx, by, bh = M, 106, 20
    total = sum(counts.values())
    x = bx
    f_rb = font(F_SANS_B, 9)
    for r in REGIONS:
        n = counts.get(r, 0)
        if n == 0:
            continue
        seg = int(round(CW * n / total))
        d.rectangle([x, by, x + seg - 1, by + bh], fill=REGION_COLORS[r])
        label = "%s %d" % (r.upper(), n)
        lw = d.textlength(label, font=f_rb)
        if lw < seg - 4:
            d.text((x + (seg - lw) / 2, by + 5), label, font=f_rb,
                   fill=(255, 255, 255))
        x += seg
    d.rectangle([bx, by, bx + CW - 1, by + bh], outline=INK, width=1)
    count_line = "39 STORIES  ·  10 REGIONS  ·  ONE PAGE"
    cw = d.textlength(count_line, font=font(F_SANS_B, 10))

    # ---- heroes: 3 cards, y 132..282
    hy0, hy1 = 132, 282
    hw, gap = 318, 11
    for i, s in enumerate(HEROES):
        x0 = M + i * (hw + gap)
        draw_card(d, x0, hy0, x0 + hw, hy1, s[0], s[1], s[2], s[3], s[4],
                  s[8], 15, 10, 8, 74)

    # ---- stat strip y 288..314
    sy0, sy1 = 288, 314
    sw = CW // 4
    f_st = font(F_SERIF_B, 15)
    f_sl = font(F_SANS, 8)
    for i, (num, lab) in enumerate(STATS):
        x0 = M + i * sw
        d.rectangle([x0, sy0, x0 + sw - 1, sy1], outline=CARD_EDGE, width=1)
        nw = d.textlength(num, font=f_st)
        lw = d.textlength(lab, font=f_sl)
        d.text((x0 + (sw - nw - lw - 8) / 2, sy0 + 5), num, font=f_st, fill=RED_DK)
        d.text((x0 + (sw - nw - lw - 8) / 2 + nw + 8, sy0 + 9), lab,
               font=f_sl, fill=INK_SOFT)

    # ---- mids: row1 7 cards (132w), row2 6 cards (156w), y 320..560
    my0, my1 = 320, 560
    row_h = 116
    row1 = MIDS[:7]
    row2 = MIDS[7:]
    for row_i, row in enumerate([row1, row2]):
        y0 = my0 + row_i * (row_h + 8)
        y1 = y0 + row_h
        n = len(row)
        cw_row = (CW - (n - 1) * 8) // n
        for i, s in enumerate(row):
            x0 = M + i * (cw_row + 8)
            draw_card(d, x0, y0, x0 + cw_row, y1, s[0], s[1], s[2], s[3],
                      s[4], s[8], 10, 8, 7, 34)

    # ---- briefs: header + 3 columns, y 566..772
    f_bh = font(F_SANS_B, 11)
    d.text((M, 566), "THE DAY IN BRIEF", font=f_bh, fill=INK)
    d.line([M + 130, 572, W - M, 572], fill=CARD_EDGE, width=1)
    f_bhl = font(F_SERIF_B, 10)
    f_bdk = font(F_SERIF, 9)
    col_w, col_gap = 314, 17
    cols = [BRIEFS[:8], BRIEFS[8:16], BRIEFS[16:]]
    brief_end = 0
    for ci, col in enumerate(cols):
        cx = M + ci * (col_w + col_gap)
        y = 582
        for (n, hl, dk, lo, la, r) in col:
            head = "%d. %s" % (n, hl)
            lines = wrap(d, head, f_bhl, col_w)
            y = text_block(d, cx, y, lines, f_bhl, INK, 11)
            dlines = wrap(d, dk, f_bdk, col_w - 6)
            y = text_block(d, cx + 6, y, dlines, f_bdk, INK_SOFT, 10)
            y += 2
        brief_end = max(brief_end, y)
    assert brief_end < 772, "briefs overflow into map: %d" % brief_end

    # ---- map + DATE CHECK: y 772..990
    map_x0, map_y0, map_x1, map_y1 = M, 772, 700, 990
    draw_map(d, img, map_x0, map_y0, map_x1, map_y1)
    dc_x0, dc_y0, dc_x1, dc_y1 = 712, 772, 1000, 990
    draw_date_check(d, dc_x0, dc_y0, dc_x1, dc_y1)

    # ---- footer
    f_ft = font(F_SANS, 8)
    foot = ("Sources: Reuters · AP · UN News · Focus Taiwan · US Treasury · "
            "CoinDesk · Yonhap · Asia Daily · NHS · European Commission · "
            "France 24 · Oxfam · NDR/WDR · All stories dated or first "
            "reported Monday 23 November 2026.")
    d.text((M, 997), foot, font=f_ft, fill=INK_SOFT)
    return img


def draw_map(d, img, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=SEA, outline=INK, width=1)
    lat_min, lat_max = -50.0, 68.2
    scale = (x1 - x0) / 360.0

    def proj(lon, lat):
        return (x0 + (lon + 180.0) * scale,
                y1 - (lat - lat_min) * scale)

    # Land and sea insets are drawn on a box-sized layer and pasted in,
    # so polygons whose points project outside the box (far north /
    # far south) can never paint over the briefs above or the footer
    # below. The layer clips exactly at the box edge.
    bw, bh = x1 - x0, y1 - y0
    layer = Image.new("RGB", (bw, bh), SEA)
    ld = ImageDraw.Draw(layer)

    def proj_l(lon, lat):
        return ((lon + 180.0) * scale,
                bh - (lat - lat_min) * scale)

    for poly in LAND:
        pts = [proj_l(lo, la) for (lo, la) in poly]
        ld.polygon(pts, fill=LAND_FILL, outline=LAND_EDGE)
    for poly in SEA_INSETS:
        pts = [proj_l(lo, la) for (lo, la) in poly]
        ld.polygon(pts, fill=SEA)
    img.paste(layer, (x0, y0))
    d.rectangle([x0, y0, x1, y1], outline=INK, width=1)

    f_map = font(F_SANS_B, 10)
    d.text((x0 + 6, y0 + 4), "THE WORLD — 39 STORIES, NUMBERED",
           font=f_map, fill=INK)

    # pins: one dot per unique location; badges per story
    locs = {}
    for s in ALL_STORIES:
        if s[5] is None:
            continue
        key = (s[5], s[6])
        locs.setdefault(key, []).append(s[0])
    dots = {}
    for (lo, la), nums in locs.items():
        px, py = proj(lo, la)
        dots[(lo, la)] = (px, py, nums)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)

    # badge solver: one unit per dot — a single badge, or a vertical
    # stack of badges when several stories share a dot (e.g. New York
    # and Washington, 6px apart). Units are placed most-constrained
    # first, greedy smallest radius first. Hard rules: 0 unit overlaps,
    # no leader crossing another unit, no unit covering any dot.
    f_b = font(F_SANS_B, 8)
    dot_list = list(dots.values())  # (px, py, nums)

    def seg_near_dot(x0s, y0s, x1s, y1s, skip_dot):
        for (qx, qy, _n) in dot_list:
            if (qx, qy) == skip_dot:
                continue
            if _seg_dist(x0s, y0s, x1s, y1s, qx, qy) < 5:
                return True
        return False

    groups = []
    for (lo, la), (px, py, nums) in dots.items():
        neigh = sum(1 for (qx, qy, _n) in dot_list
                    if (qx - px) ** 2 + (qy - py) ** 2 < 90 ** 2)
        groups.append((-len(nums), -neigh, min(nums), px, py, nums))
    groups.sort()

    def solve(order):
        """Greedy placement for one ordering. Returns (placed, None) on
        success, (None, failed_nums) on the first dot with no slot."""
        placed = []  # (x0,y0,x1,y1, label, cx, cy, px, py)
        for (_a, _b, _c, px, py, nums) in order:
            labels = [str(n) for n in nums]
            bw = max(12, max(d.textlength(t, font=f_b) for t in labels) + 5)
            bh = 12 * len(labels) + 2 * (len(labels) - 1)
            best = None
            for radius in (12, 16, 20, 24, 30, 38, 48, 60, 76, 92, 110):
                for ang in range(0, 360, 5):
                    a = math.radians(ang)
                    cx = px + radius * math.cos(a)
                    cy = py + radius * math.sin(a)
                    bx0, by0 = cx - bw / 2, cy - bh / 2
                    bx1, by1 = cx + bw / 2, cy + bh / 2
                    if bx0 < x0 + 2 or by0 < y0 + 16 or bx1 > x1 - 2 or by1 > y1 - 2:
                        continue
                    if any(not (bx1 < p[0] - 1 or bx0 > p[2] + 1 or
                                by1 < p[1] - 1 or by0 > p[3] + 1) for p in placed):
                        continue
                    # unit must not cover any dot
                    if any(bx0 <= qx <= bx1 and by0 <= qy <= by1
                           for (qx, qy, _n) in dot_list):
                        continue
                    # leader must not cross a placed unit nor pass near a dot
                    if any(_seg_hits_rect(cx, cy, px, py, p) for p in placed):
                        continue
                    if seg_near_dot(cx, cy, px, py, (px, py)):
                        continue
                    best = (bx0, by0, bx1, by1, cx, cy)
                    break
                if best:
                    break
            if best is None:
                return None, nums
            bx0, by0, bx1, by1, cx, cy = best
            placed.append((bx0, by0, bx1, by1, ",".join(labels),
                           cx, cy, px, py))
        return placed, None

    # Greedy order is not always feasible: an early unit can box in a
    # later dot (e.g. Brussels' unit landing under Frankfurt's dot).
    # Deterministic retry: move the failed dot to the front and try
    # again, up to one retry per dot.
    placed, failed = solve(groups)
    tries = 0
    while placed is None and tries < len(groups):
        retry = [g for g in groups if g[5] == failed] + \
            [g for g in groups if g[5] != failed]
        placed, failed = solve(retry)
        tries += 1
    if placed is None:
        raise RuntimeError("no badge slot for dot %s" % (failed,))

    # draw leaders + badges from the solved placements
    for (bx0, by0, bx1, by1, label, cx, cy, px, py) in placed:
        # leader: dark underlay then white core
        d.line([cx, cy, px, py], fill=RED_DK, width=3)
        d.line([cx, cy, px, py], fill=(255, 255, 255), width=1)
        for i, t in enumerate(label.split(",")):
            ry0 = by0 + i * 14
            d.rectangle([bx0, ry0, bx1, ry0 + 12], fill=INK)
            d.text((cx - d.textlength(t, font=f_b) / 2, ry0 + 2), t,
                   font=f_b, fill=(255, 255, 255))

    # verify: 0 overlaps between units
    for i, p in enumerate(placed):
        for q in placed[i + 1:]:
            assert p[2] < q[0] or p[0] > q[2] or p[3] < q[1] or p[1] > q[3], \
                "badge overlap: %s vs %s" % (p[4], q[4])

    f_fn = font(F_SANS, 8)
    d.text((x0 + 6, y1 - 12),
           "1 = SEA (off Benghazi)  ·  9 = GLOBAL (no dot)",
           font=f_fn, fill=INK_SOFT)
    return placed


def _seg_dist(x0, y0, x1, y1, px, py):
    """Distance from point (px,py) to segment (x0,y0)-(x1,y1)."""
    dx, dy = x1 - x0, y1 - y0
    if dx == 0 and dy == 0:
        return math.hypot(px - x0, py - y0)
    t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))


def _seg_hits_rect(x0, y0, x1, y1, rect):
    """True if segment (x0,y0)-(x1,y1) crosses rect (rx0,ry0,rx1,ry1)."""
    rx0, ry0, rx1, ry1 = rect[:4]
    def inside(px, py):
        return rx0 <= px <= rx1 and ry0 <= py <= ry1
    if inside(x0, y0) or inside(x1, y1):
        return True
    def cross(ax, ay, bx, by, cx, cy, dx, dy):
        den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
        if den == 0:
            return False
        t = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den
        u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
        return 0 <= t <= 1 and 0 <= u <= 1
    edges = [(rx0, ry0, rx1, ry0), (rx1, ry0, rx1, ry1),
             (rx1, ry1, rx0, ry1), (rx0, ry1, rx0, ry0)]
    return any(cross(x0, y0, x1, y1, *e) for e in edges)


def draw_date_check(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(255, 246, 244), outline=RED, width=2)
    f_h = font(F_SANS_B, 11)
    d.text((x0 + 8, y0 + 6), "DATE CHECK — EXCLUDED", font=f_h, fill=RED_DK)
    f_i = font(F_SERIF, 9)
    f_dt = font(F_SANS_B, 9)
    y = y0 + 24
    for (name, when) in DATE_CHECK:
        d.text((x0 + 8, y), "×  " + name, font=f_i, fill=INK)
        w = d.textlength(when, font=f_dt)
        d.text((x1 - 8 - w, y), when, font=f_dt, fill=RED_DK)
        y += 14
    f_n = font(F_SANS, 8)
    note = "All stories above are dated Monday 23 November 2026."
    for ln in wrap(d, note, f_n, x1 - x0 - 16):
        d.text((x0 + 8, y), ln, font=f_n, fill=INK_SOFT)
        y += 10
    assert y <= y1 - 4, "DATE CHECK note overflows: %d > %d" % (y, y1)


def verify():
    """Programmatic checks; raises on failure."""
    # story count + numbering
    nums = [s[0] for s in ALL_STORIES]
    assert nums == list(range(1, 40)), "numbering broken: %s" % nums
    # regions sum
    counts = {}
    for s in ALL_STORIES:
        counts[s[7]] = counts.get(s[7], 0) + 1
    assert sum(counts.values()) == 39, counts
    # pins on land (except footnoted sea/global)
    bad = []
    for s in ALL_STORIES:
        if s[5] is None:
            continue
        if s[0] == 1:  # sea story, footnoted
            continue
        if not on_land(s[5], s[6]):
            bad.append((s[0], s[5], s[6]))
    assert not bad, "pins off land: %s" % bad
    return counts


if __name__ == "__main__":
    import sys
    counts = verify()
    print("regions:", counts)
    img = render()
    img.save(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
    print("saved", img.size)
