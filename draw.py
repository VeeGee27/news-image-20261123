#!/usr/bin/env python3
"""Draw the news-image-20261123 v1 front page: one image summing up
Monday 23 November 2026 in world news. PIL only, deterministic output.
Writes entry.png (1024x1024) next to this file."""

import hashlib
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

PAPER = (243, 235, 214)
PAPER_DARK = (231, 221, 195)
INK = (28, 24, 19)
INK_SOFT = (74, 66, 54)
RED = (172, 28, 28)
RED_DARK = (140, 20, 20)
RULE = (120, 104, 78)
LAND = (205, 184, 134)
LAND_EDGE = (138, 116, 76)
SEA = (216, 228, 219)
GRID = (198, 206, 195)

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DSERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


F_MAST = font(DSERIF_B, 42)
F_DATE = font(SANS_B, 10)
F_STAT_N = font(SERIF_B, 17)
F_STAT_L = font(SANS_B, 8)
F_KICK = font(SANS_B, 9)
F_HERO_H = font(SERIF_B, 17)
F_HERO_T = font(SERIF, 11)
F_TAG = font(SANS_B, 8)
F_MID_H = font(SERIF_B, 12)
F_MID_T = font(SERIF, 9)
F_BRIEF_H = font(SANS_B, 11)
F_BRIEF = font(SERIF, 10)
F_BRIEF_N = font(SERIF_B, 10)
F_REGION = font(SANS_B, 9)
F_MAP_T = font(SANS_B, 10)
F_DC_T = font(SANS_B, 10)
F_DC = font(SERIF, 10)
F_DC_B = font(SERIF_B, 10)
F_FOOT = font(SANS, 8)
F_BADGE = font(SANS_B, 9)
F_NOTE = font(SERIF, 9)
F_NOTE_B = font(SERIF_B, 9)

# ---------------------------------------------------------------- stories
# (number, region, lat, lon, kicker, headline, text, tag, art)

HEROES = [
    (1, "Europe", 50.85, 4.35, "SECURITY  ·  BRUSSELS",
     "NATO MEETS AS POLAND CONFIRMS RUSSIAN MISSILES",
     "All three cruise missiles that fell on Friday were Russian Kh-101s, prosecutors said on Sunday. The North Atlantic Council gathers in Brussels today; PM Tusk called the incursion an \u201cintentional provocation\u201d.",
     "CONFIRMED \u2014 NATO / AP", "nato"),
    (2, "Asia", 25.03, 121.57, "MARKETS  ·  TAIPEI",
     "TAIWAN BANS SHORT SELLING AS ASIA ROUT DEEPENS",
     "Taipei barred short sales below the prior close from today after the Taiex lost 18% last week, its worst in 35 years. Seoul\u2019s Kospi slid 3.8% as Korea readied a 10 trillion won stabilisation fund.",
     "CONFIRMED \u2014 REUTERS", "chart"),
    (3, "Oceania", -41.29, 174.78, "CRICKET  ·  WELLINGTON",
     "INDIA\u2019S RECORD 720 DENIED AS TEST ENDS IN A DRAW",
     "New Zealand held on at 239 for 5 \u2014 Mitchell 49 not out \u2014 after India\u2019s 720 for 9 declared, built on Rahul\u2019s 136 and Pant\u2019s 128. The draw drops New Zealand to third in the Test championship.",
     "CONFIRMED \u2014 IANS", "cricket"),
]

MIDS = [
    (4, "Oceania", -13.66, 172.24, "M6.5 QUAKE STRIKES OFF VANUATU",
     "A magnitude 6.5 quake struck at 02:40 UTC, 601 km deep. No tsunami threat was issued.",
     "CONFIRMED \u2014 USGS", "quake"),
    (5, "Europe", 52.20, 0.12, "NHS LAUNCHES WORLD\u2019S LARGEST AI BREAST-SCREENING TRIAL",
     "Some 700,000 women at 30 sites will be screened with AI over three years in the \u00a311m EDITH trial; recruitment began in Cambridge.",
     "CONFIRMED \u2014 BBC", "health"),
    (6, "Asia", 28.61, 77.21, "NEPAL PM BALEN SHAH WELCOMED IN DELHI",
     "Shah received a welcome at Rashtrapati Bhavan and holds delegation talks with PM Modi today, his first bilateral visit since March.",
     "CONFIRMED \u2014 THE HINDU", "mountain"),
    (7, "Europe", 47.38, 8.54, "FIFA CONFIRMS UK AS 2035 WOMEN\u2019S WORLD CUP HOST",
     "England, Scotland, Wales and Northern Ireland will stage the first World Cup in Britain since 1966: 48 teams, 104 matches, 19 venues.",
     "CONFIRMED \u2014 BBC", "football"),
    (8, "Europe", 50.78, 30.31, "BOY, 7, PULLED ALIVE FROM RUBBLE IN DIMER",
     "Rescuers freed the boy hours after a Russian strike collapsed a home in the Kyiv region; nine people were killed.",
     "CONFIRMED \u2014 BBC", "rescue"),
    (9, "Europe", 46.48, 30.73, "ODESA SCHOOLS GO REMOTE AS GRID LIES IN RUINS",
     "Schools switch to online learning from 23 to 27 November after Russian strikes damaged the power grid.",
     "REPORTED \u2014 ODESA OFFICIALS", "school"),
    (10, "Asia", 28.00, 94.50, "INDIA, CHINA OPEN 10 DAYS OF BORDER TALKS",
     "Military commanders meet in Arunachal Pradesh to ease tensions along the Line of Actual Control.",
     "CONFIRMED \u2014 THE HINDU", "mountain"),
    (11, "North America", 40.83, -91.26, "ARMY TO DETONATE LEAD AZIDE DESPITE COURT PAUSE",
     "The US Army invoked emergency powers to destroy 68 barrels of unstable explosive in Iowa by Tuesday, bypassing a court-ordered freeze.",
     "CONFIRMED \u2014 AP", "barrel"),
    (12, "Europe", 41.90, 12.50, "PAOLO BULGARI DIES AT 89",
     "The Italian jeweller who turned the family house into a global luxury name has died in Rome.",
     "CONFIRMED \u2014 BBC", "jewel"),
    (13, "Europe", 48.86, 2.35, "FRENCH STUDENTS PLAN NATIONWIDE PROTESTS",
     "Pupils prepare to march against the government\u2019s education reforms in a new wave of demonstrations.",
     "REPORTED \u2014 FRENCH MEDIA", "protest"),
    (14, "Europe", 52.08, 4.31, "DUTCH FM: INDIA CAN HELP END UKRAINE WAR",
     "Foreign minister Tom Berendsen said New Delhi\u2019s engagement with Moscow could help bring the war to an end.",
     "REPORTED \u2014 DUTCH FM", "dove"),
    (15, "North America", 37.77, -122.42, "OPENAI SCIENTIST URGES COMMON AI LIMITS",
     "A leading researcher called for shared safety rules, warning of serious risks from advanced AI by 2027.",
     "REPORTED \u2014 OPENAI SCIENTIST", "ai"),
    (16, "Asia", 3.07, 101.52, "SELANGOR FLOOD EVACUEES FALL TO 1,594",
     "Waters receded in Kuala Selangor and Kuala Langat, leaving 448 families in 12 relief centres.",
     "CONFIRMED \u2014 MEDIA SELANGOR", "flood"),
]

BRIEFS = [
    (17, "Asia", 13.26, 123.69, "Mayon stays at Alert Level 3 in PHIVOLCS\u2019 23 Nov update."),
    (18, "Oceania", -33.87, 151.21, "Albanese: COP31 failure a sign of \u201cdifficult geopolitical times\u201d."),
    (19, "North America", 38.91, -77.04, "1,389 Indian children taken into US custody since 2023."),
    (20, "Asia", 37.57, 126.98, "Kospi slides 3.76% as Seoul readies a 10tn won stabilisation fund."),
    (21, "Asia", 39.90, 116.41, "China to cut stock margin ratio to 80% from 30 November."),
    (22, "Asia", 35.68, 139.69, "Japan markets shut for Labour Thanksgiving Day."),
    (23, "Asia", 36.48, 127.29, "Seoul files criminal cases against five in AI exam-cheating scandal."),
    (24, "Asia", 30.73, 76.78, "Congress MLA writes letter in blood to Haryana CM, briefly detained."),
    (25, "Asia", 22.57, 88.36, "West Bengal BJP calls protest over attacks on Hindus in Bangladesh."),
    (26, "Asia", 28.63, 77.23, "Food regulator orders prosecution of Bisleri over unsafe water."),
    (27, "Europe", 51.51, -0.13, "UK energy bills will soar, households warned."),
    (28, "Europe", 53.48, -2.24, "Tyson Fury reveals schizophrenia diagnosis in documentary."),
    (29, "Europe", 51.39, -0.51, "Compass to move its stock-market listing to New York."),
    (30, "Europe", 51.50, -0.12, "UK plans universal-credit reform to push people into work."),
    (31, "Europe", 51.52, -0.14, "Disability benefits review to recommend payment changes."),
    (32, "Europe", 46.20, 6.14, "Sindarov gets white pieces for Tuesday\u2019s World Championship Game 1."),
    (33, "North America", 35.49, -80.62, "Rafael Camara stays with Haas for the final two grands prix."),
    (34, "North America", 38.90, -77.03, "US intelligence chief trusts Trump\u2019s \u201cmy friend\u201d Putin description."),
    (35, "Africa", 32.12, 20.07, "Libya suspects drone attack caused blast on Russian ship at Benghazi."),
    (36, "Europe", 53.47, -2.23, "Pochettino demands response after Man Utd\u2019s 4\u20130 Anfield defeat."),
    (37, "Asia", 26.85, 80.95, "Syed Modi badminton build-up begins in Lucknow."),
    (38, "Asia", 13.76, 100.50, "Thai anti-graft body to hear gold-bribery case."),
    (39, "Asia", 13.75, 100.52, "Thai police probe human remains found in Bangkok."),
]

STATS = [
    ("700,000", "WOMEN IN NHS AI TRIAL"),
    ("6.5", "MAGNITUDE, VANUATU QUAKE"),
    ("48", "TEAMS AT 2035 WORLD CUP"),
    ("1,594", "FLOOD EVACUEES, SELANGOR"),
    ("10", "DAYS OF INDIA\u2013CHINA TALKS"),
    ("1,389", "CHILDREN IN US CUSTODY"),
]

DATE_CHECK = [
    ("Democrats\u2019 258 House seats", "called Sun 22 Nov"),
    ("COP31 climate talks collapse", "Sun 22 Nov"),
    ("Russian ship blast, Benghazi", "Sun 22 Nov"),
    ("Liverpool 4\u20130 Man Utd", "Sun 22 Nov"),
    ("Alcaraz wins ATP Finals", "Sun 22 Nov"),
    ("Barcelona 3\u20132 Villarreal", "Sun 22 Nov"),
    ("Korea education minister quits", "Sun 22 Nov"),
    ("ICE detains father & daughter, Seattle", "Sat 21 Nov"),
]

REGIONS = [
    ("EUROPE", 15, (140, 28, 28)),
    ("ASIA", 15, (28, 64, 120)),
    ("N. AMERICA", 5, (36, 110, 66)),
    ("OCEANIA", 3, (196, 120, 28)),
    ("AFRICA", 1, (110, 62, 140)),
]

# Badge offsets (px) for clustered map dots, to keep badges from overlapping.
BADGE_OFF = {
    1: (-26, 8), 5: (16, -20), 6: (20, -16), 7: (20, -14),
    8: (20, -12), 9: (-22, 14), 10: (16, -12), 12: (18, 14),
    13: (-26, -10), 14: (22, -14), 19: (20, -14), 20: (22, -16),
    23: (-24, 12), 24: (-24, -12), 25: (-14, 10), 26: (-22, 14),
    27: (-26, -14), 28: (20, -14), 29: (-28, 16), 30: (24, 10),
    31: (26, -16), 32: (-22, 12), 33: (-24, 14), 34: (-22, 12),
    36: (-22, 12), 37: (24, 12), 38: (20, -14), 39: (-22, 12),
}

ALL_STORIES = HEROES + [
    (n, r, la, lo, "", h, t, tag, a) for (n, r, la, lo, h, t, tag, a) in MIDS
] + [
    (n, r, la, lo, "", b, "", "", "") for (n, r, la, lo, b) in BRIEFS
]

# ---------------------------------------------------------------- map data
# Simplified coastline polygons as (lon, lat) pairs, drawn fresh here.

NORTH_AMERICA = [
    (-168, 66), (-165, 60), (-158, 58), (-152, 60), (-145, 60), (-140, 60),
    (-135, 58), (-130, 55), (-125, 49), (-124, 42), (-120, 34), (-114, 29),
    (-110, 24), (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-87, 13),
    (-83, 9), (-80, 9), (-77, 8), (-80, 10), (-83, 15), (-86, 16),
    (-88, 18), (-90, 21), (-91, 19), (-94, 19), (-97, 22), (-97, 26),
    (-93, 30), (-89, 30), (-85, 30), (-84, 30), (-82.7, 28), (-81.8, 26),
    (-80.2, 25.2), (-80.1, 27), (-81.0, 29.5), (-81.3, 30.4), (-81.5, 31),
    (-80, 32.2), (-79, 33), (-76, 35), (-75.5, 37), (-74, 39.5), (-70, 41.5),
    (-70.5, 43), (-68.5, 44.5), (-65.5, 44), (-64, 44.5), (-60, 46),
    (-59.5, 47.5), (-55.5, 47), (-53, 48.5), (-56, 50), (-60, 51),
    (-64, 50), (-66, 52), (-60, 55), (-64, 58), (-68, 58.5), (-70, 60),
    (-74, 62), (-78, 62.5), (-82, 66), (-85, 66), (-90, 66), (-92, 66),
    (-95, 69), (-100, 68.5), (-110, 68), (-115, 69.5), (-125, 70),
    (-135, 69.5), (-140, 70), (-148, 70.5), (-155, 71), (-162, 71),
    (-166, 68), (-168, 65.5),
]

SOUTH_AMERICA = [
    (-80, 9), (-77, 4), (-77, -3), (-80, -6), (-81, -12), (-77, -18),
    (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
    (-66, -55), (-65, -50), (-62, -45), (-58, -38), (-52, -33), (-48, -28),
    (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
    (-50, 0), (-52, 4), (-55, 6), (-60, 8), (-62, 10), (-65, 11),
    (-70, 12), (-75, 11), (-77, 8), (-80, 9),
]

AFRICA = [
    (-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-16, 12),
    (-13, 8), (-8, 5), (-4, 5), (1, 6), (6, 4), (9, 4), (9, 0),
    (12, -4), (13, -10), (12, -17), (14, -22), (16, -28), (18, -34),
    (20, -35), (26, -34), (28, -33), (32, -29), (35, -24), (36, -18),
    (40, -15), (40, -10), (42, -5), (46, -1), (51, 2), (51, 11),
    (48, 11.5), (44, 11), (43, 12.5), (40, 15), (38, 18), (37, 22),
    (35, 28), (34, 28), (32, 31), (30, 31.5), (25, 32), (20, 32),
    (15, 32.5), (11, 34), (10, 37), (5, 37), (0, 36), (-6, 35),
]

EURASIA = [
    (-9.5, 37), (-9.5, 43), (-2, 43.7), (-1.8, 46), (-4.8, 48.5), (-1, 49.5),
    (1.5, 51), (3.5, 51.5), (5, 53.5), (7, 54), (8, 57), (10, 58),
    (12, 56), (18, 56), (21, 55), (21, 59), (24, 59.5), (28, 60),
    (30, 62), (32, 66), (35, 67), (40, 67.5), (45, 68), (50, 69),
    (55, 68.5), (60, 69), (65, 69.5), (70, 72), (75, 72.5), (80, 73),
    (85, 74), (90, 75), (95, 76), (100, 76.5), (105, 77), (110, 74),
    (115, 73), (120, 73.5), (125, 72), (130, 71), (135, 71.5), (140, 72),
    (145, 71), (150, 70), (155, 69.5), (160, 69), (165, 66), (170, 66),
    (178, 65), (180, 66), (178, 64), (170, 60), (162, 58), (158, 53),
    (156, 51), (150, 59), (142, 55), (141, 50), (140, 45), (138, 40),
    (135, 35), (130, 33), (127, 35), (126, 38), (124.5, 40), (122, 39),
    (120, 35), (122, 31), (121, 28), (120, 24), (118, 24.5), (116, 23),
    (113, 22), (110, 20), (108, 18.5), (106, 20), (105, 21), (103, 16),
    (100, 13), (98, 10), (97, 8), (99, 7), (101, 5), (103, 2),
    (104, 1.5), (103.5, 4), (101, 6.5), (99, 9), (98.5, 12.5),
    (97.5, 15.5), (94.5, 17.5), (92.5, 21), (91, 22.5), (89, 22),
    (88, 21.7), (86, 20), (84, 18.5), (82, 16.5), (80.5, 13.5),
    (80.3, 10), (79.5, 8.5), (77.5, 8.1), (76, 10), (74.5, 14),
    (73, 17), (72.8, 20), (70, 21), (68, 22.5), (66.5, 25), (64, 25.2),
    (61, 25.2), (58, 25.5), (56.5, 26.5), (54, 26.5), (52, 25.8),
    (50.5, 26.5), (50, 29), (48.5, 29.5), (48, 30), (49, 30.5),
    (51, 28.5), (54, 26.8), (56, 27), (57.5, 25.8), (59, 22.5),
    (58.5, 20.5), (55, 17.5), (52, 15.5), (48, 14), (45, 12.8),
    (43.5, 12), (42, 13.5), (41, 16), (39.5, 20), (38.5, 24),
    (36.5, 28), (35, 29), (34.5, 28), (34, 27.5), (35.5, 31.5),
    (36, 36), (33, 36.2), (30, 36.3), (27.5, 37), (26, 38.5),
    (23.5, 36.5), (23, 40), (22.5, 40.5), (19.5, 42), (18, 40.5),
    (16, 41.5), (14, 42.5), (12.5, 44), (10.5, 44), (8, 44),
    (6, 43), (3.5, 42.5), (3, 41.5), (0, 39), (-0.5, 37), (-2, 36.7),
    (-5.5, 36), (-7, 37.2), (-8.9, 37), (-9.5, 38.5), (-9, 42),
]

UK = [
    (-5.5, 50), (-3, 50.5), (-1.5, 50.8), (0, 51.3), (1.5, 51.5),
    (1, 52.5), (0.5, 53), (-0.5, 53.5), (-2, 55), (-3, 56), (-5, 58),
    (-6, 58.5), (-5, 57), (-4, 55), (-3, 53.5), (-5, 52), (-5.5, 51),
]
IRELAND = [
    (-10, 52), (-8, 51.5), (-6, 52), (-5.5, 53.5), (-6, 55), (-8, 55),
    (-10, 54),
]
HOKKAIDO = [
    (140, 42), (141, 42.5), (143, 42.5), (145, 43.5), (145.5, 44),
    (143, 44.5), (141.5, 45.5), (140, 44.5), (139.5, 42.5),
]
HONSHU = [
    (130, 31.5), (131, 33), (133, 34), (135, 34.5), (137, 35), (139, 35),
    (140, 36.5), (141, 38), (141, 40), (140, 41.5), (139.5, 40),
    (137, 38), (135, 36), (133, 35.5), (131, 34), (130, 33), (129.5, 32),
]
KYUSHU = [
    (129.5, 31), (130, 32), (131, 33.5), (131.5, 32), (130.5, 31),
]
SHIKOKU = [(133, 33.5), (134, 34), (135, 34), (134, 33.5)]
TAIWAN = [
    (120.1, 25.3), (121, 25.3), (121.9, 25), (121, 23.5),
    (120.9, 22.6), (120.1, 22.7), (120, 24),
]
KOREA = [
    (124.5, 39.5), (126, 38), (127.5, 38.5), (129.5, 38), (129.5, 36),
    (129, 35), (127.5, 34.8), (126.5, 34.8), (126, 36), (124.8, 37.5),
]
LUZON = [
    (119.9, 18.2), (122, 18.5), (122.2, 16.5), (124, 14), (122.5, 13.8),
    (121, 13.5), (120.5, 14.5), (119.9, 16),
]
MINDANAO = [
    (122, 7.8), (124, 8.5), (126, 7.5), (126.5, 6.5), (124, 6),
    (122.5, 7),
]
PALAWAN = [(117, 8.5), (119, 10), (119.5, 11), (117.5, 10.5)]
SUMATRA = [
    (95, 5.5), (97, 4), (100, 0), (103, -2), (105, -4), (106, -6),
    (104, -5.5), (102, -3), (100, -1), (98, 2), (95.5, 5),
]
JAVA = [
    (105.5, -6), (108, -7), (111, -7), (114, -8), (114.5, -8.5),
    (112, -7.5), (109, -7), (106.5, -6.5),
]
BORNEO = [
    (109, 1), (110, 2), (113, 4), (116, 6), (118, 2), (117, -1),
    (116, -3.5), (114, -3.5), (111, -3), (109.5, -1),
]
SULAWESI = [
    (119, 0), (120.5, 1), (123, 1), (123.5, -1), (121, -3), (120, -5),
    (119.5, -5.5), (119, -3),
]
NEW_GUINEA = [
    (131, -1), (133, -2), (136, -2.5), (138, -4), (141, -6), (144, -7),
    (147, -9), (150, -10), (146, -8), (143, -8.5), (141, -8), (138, -7),
    (136, -4.5), (133, -3),
]
SRI_LANKA = [
    (79.8, 9), (80.8, 9.5), (81.9, 8.5), (81.5, 6.5), (80, 6), (79.8, 8),
]
MADAGASCAR = [
    (43.5, -12), (44, -16), (47, -15), (50, -16), (50, -20), (47, -24),
    (45, -25.5), (43.5, -21), (43.5, -16),
]
AUSTRALIA = [
    (113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
    (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
    (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
    (146, -19), (142, -15), (142, -11), (137, -12), (136, -15),
    (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
    (118, -20), (114, -22),
]
TASMANIA = [(145, -41), (148, -41), (148, -43), (146, -43.5), (145, -42)]
NZ_NORTH = [
    (173, -35), (175, -36.5), (178, -38), (177.5, -39.5), (175, -40),
    (174, -41.5), (173, -40), (173.5, -37),
]
NZ_SOUTH = [
    (168, -44), (167, -45.5), (168.5, -46.5), (170, -44), (173, -43),
    (174, -41.5), (172.5, -41), (170, -42.5),
]

LAND_POLYS = [
    NORTH_AMERICA, SOUTH_AMERICA, AFRICA, EURASIA, UK, IRELAND,
    HOKKAIDO, HONSHU, KYUSHU, SHIKOKU, TAIWAN, KOREA, LUZON,
    MINDANAO, PALAWAN, SUMATRA, JAVA, BORNEO, SULAWESI, NEW_GUINEA,
    SRI_LANKA, MADAGASCAR, AUSTRALIA, TASMANIA, NZ_NORTH, NZ_SOUTH,
]

# Inland seas drawn back over the land fill, in sea colour.
MEDITERRANEAN = [
    (-5.5, 36), (-2, 36.7), (0, 38), (3, 39), (6, 38), (8, 39), (10, 38.5),
    (11, 37), (12.5, 38), (15, 38.5), (16, 40), (18, 40), (19.5, 40.5),
    (21, 39), (23, 36.5), (24, 36), (26, 36.5), (28, 36.5), (30, 36.3),
    (32, 36.2), (34, 36), (36, 36.2), (35.8, 34), (35.5, 32), (34.3, 29),
    (34, 28), (33, 29), (32.5, 31.3), (31, 31.5), (29, 31), (26, 32),
    (24, 32.5), (22, 33), (20, 32.5), (18, 33), (15, 32.5), (12, 33.5),
    (11, 34.5), (10, 36), (8, 37), (5, 37), (3, 37.5), (0, 36.5),
    (-3, 35.8), (-5.5, 35.9),
]
BLACK_SEA = [
    (28, 41), (30, 41.5), (33, 42), (35, 42), (38, 41.5), (39, 41),
    (41, 41.5), (41.5, 43), (39, 44), (36, 44.5), (34, 44.8), (32, 44.5),
    (31, 45), (29, 45.5), (28, 43.5),
]
CASPIAN = [
    (47, 37), (49, 38), (51, 40), (52, 42), (53, 44), (52, 46),
    (50, 47), (48, 46.5), (47, 44), (46.5, 42), (47, 39),
]
PERSIAN_GULF = [
    (48, 30), (50, 29), (52, 27), (54, 26.5), (56, 26.5), (57, 25.5),
    (55, 25), (52, 25.5), (50, 26.5), (48.5, 29),
]
RED_SEA = [
    (35, 28), (36, 26), (37, 23), (38, 20), (39, 17), (40, 15),
    (41, 13), (43, 12.5), (42, 14), (40, 17), (38.5, 21), (37, 24),
    (36, 27),
]
BALTIC = [
    (10, 54), (12, 55), (15, 55), (18, 56), (21, 57), (23, 58),
    (24, 59.5), (23, 60), (21, 60), (19, 59), (17, 58), (13, 55),
]
LAKE_SUPERIOR = [
    (-92, 47), (-88, 47.5), (-85, 46.5), (-84, 46), (-88, 46.5), (-90, 47),
]
LAKE_MICHIGAN = [(-87, 42), (-86, 44), (-87, 46), (-88, 44)]
LAKE_HURON = [(-82, 44), (-80, 44.5), (-79, 45), (-82, 46), (-84, 45)]
LAKE_ERIE = [(-83, 42), (-80, 42.5), (-79, 43), (-80, 42)]

SEA_POLYS = [
    MEDITERRANEAN, BLACK_SEA, CASPIAN, PERSIAN_GULF, RED_SEA, BALTIC,
    LAKE_SUPERIOR, LAKE_MICHIGAN, LAKE_HURON, LAKE_ERIE,
]

# ---------------------------------------------------------------- helpers

def wrap(d, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_center(d, cx, y, text, fnt, fill):
    w = d.textlength(text, font=fnt)
    d.text((cx - w / 2, y), text, font=fnt, fill=fill)


def rule(d, x0, x1, y, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def paper_texture(d):
    rng = random.Random(20261123)
    for _ in range(2600):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        shade = rng.choice([(238, 229, 206), (247, 240, 222), (235, 226, 202)])
        d.point((x, y), fill=shade)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(242, 234, 213), width=1)

# ---------------------------------------------------------------- art
# Small drawn illustrations, one per art key. All shapes are placed
# relative to the given box so the same art works in the tall hero
# panels and in the smaller mid-card panels. Nothing draws outside
# its box.

import math


def art_nato(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(28, 52, 88))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = min(x1 - x0, y1 - y0) / 2 - 4
    star = [(cx, cy - r), (cx + r * 0.22, cy - r * 0.22), (cx + r, cy),
            (cx + r * 0.22, cy + r * 0.22), (cx, cy + r),
            (cx - r * 0.22, cy + r * 0.22), (cx - r, cy),
            (cx - r * 0.22, cy - r * 0.22)]
    d.polygon(star, fill=(255, 255, 255))
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(172, 28, 28))


def art_chart(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(246, 241, 228))
    w, h = x1 - x0, y1 - y0
    d.line([(x0 + w * 0.06, y1 - h * 0.16), (x1 - w * 0.04, y1 - h * 0.16)],
           fill=RULE, width=1)
    d.line([(x0 + w * 0.06, y0 + h * 0.12), (x0 + w * 0.06, y1 - h * 0.16)],
           fill=RULE, width=1)
    pts = []
    for i in range(6):
        px = x0 + w * 0.12 + i * (w * 0.80) / 5
        py = y0 + h * 0.16 + i * (h * 0.62) / 5
        pts.append((px, py))
    d.line(pts, fill=RED, width=2)
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)


def art_cricket(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(46, 110, 66))
    w, h = x1 - x0, y1 - y0
    cx = x0 + w / 2
    d.rectangle([cx - w * 0.03, y0 + h * 0.08, cx + w * 0.03, y1 - h * 0.08],
                fill=(232, 220, 180))
    for dx in (-w * 0.018, 0, w * 0.018):
        d.line([(cx + dx, y0 + h * 0.14), (cx + dx, y0 + h * 0.38)],
               fill=(250, 220, 90), width=2)
    d.line([(x0 + w * 0.06, y1 - h * 0.16), (x1 - w * 0.06, y1 - h * 0.16)],
           fill=(255, 255, 255), width=1)
    d.ellipse([x1 - w * 0.07, y1 - h * 0.30, x1 - w * 0.04, y1 - h * 0.14],
              fill=(172, 28, 28))


def art_quake(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(40, 36, 32))
    w, h = x1 - x0, y1 - y0
    mid = y0 + h / 2
    amps = [0, 0.06, -0.10, 0.22, -0.38, 0.44, -0.24, 0.14, -0.10, 0.07,
            -0.04, 0.02, 0]
    pts = []
    for i, a in enumerate(amps):
        px = x0 + w * 0.04 + i * (w * 0.92) / (len(amps) - 1)
        pts.append((px, mid + a * h))
    d.line([(x0 + w * 0.03, mid), (x1 - w * 0.03, mid)],
           fill=(120, 110, 100), width=1)
    d.line(pts, fill=(220, 80, 60), width=2)


def art_health(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(245, 225, 228))
    w, h = x1 - x0, y1 - y0
    cx, cy = x0 + w / 2, y0 + h / 2
    r = min(w, h) / 2 - 3
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    d.rectangle([cx - 2.5, cy - r + 4, cx + 2.5, cy + r - 4], fill=RED)
    d.rectangle([cx - r + 4, cy - 2.5, cx + r - 4, cy + 2.5], fill=RED)


def art_mountain(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(200, 220, 235))
    w, h = x1 - x0, y1 - y0
    d.ellipse([x1 - w * 0.14, y0 + h * 0.10,
               x1 - w * 0.04, y0 + h * 0.10 + w * 0.10],
              fill=(250, 220, 120))
    d.polygon([(x0 + w * 0.04, y1 - 2), (x0 + w * 0.34, y0 + h * 0.22),
               (x0 + w * 0.60, y1 - 2)], fill=(90, 110, 130))
    d.polygon([(x0 + w * 0.44, y1 - 2), (x0 + w * 0.72, y0 + h * 0.30),
               (x1 - w * 0.04, y1 - 2)], fill=(60, 80, 100))
    d.polygon([(x0 + w * 0.34, y0 + h * 0.22), (x0 + w * 0.28, y0 + h * 0.38),
               (x0 + w * 0.40, y0 + h * 0.38)], fill=(255, 255, 255))
    d.polygon([(x0 + w * 0.72, y0 + h * 0.30), (x0 + w * 0.67, y0 + h * 0.44),
               (x0 + w * 0.77, y0 + h * 0.44)], fill=(255, 255, 255))


def art_football(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(56, 120, 70))
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3],
                outline=(255, 255, 255), width=1)
    d.line([(x0 + w / 2, y0 + 3), (x0 + w / 2, y1 - 3)],
           fill=(255, 255, 255), width=1)
    d.ellipse([x0 + w / 2 - h * 0.22, y0 + h * 0.28,
               x0 + w / 2 + h * 0.22, y0 + h * 0.72],
              outline=(255, 255, 255), width=1)
    d.ellipse([x1 - w * 0.10, y1 - h * 0.28, x1 - w * 0.04, y1 - h * 0.06],
              fill=(255, 255, 255))
    d.ellipse([x1 - w * 0.082, y1 - h * 0.20, x1 - w * 0.058, y1 - h * 0.14],
              fill=(28, 24, 19))


def art_rescue(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(60, 55, 50))
    w, h = x1 - x0, y1 - y0
    d.polygon([(x0 + w * 0.10, y0 + 2), (x0 + w * 0.32, y0 + 2),
               (x0 + w * 0.46, y1 - h * 0.55), (x0 + w * 0.22, y1 - h * 0.55)],
              fill=(250, 230, 150))
    blocks = [(0.06, 0.62, 0.22, 0.16), (0.30, 0.55, 0.24, 0.18),
              (0.58, 0.66, 0.22, 0.14), (0.10, 0.82, 0.26, 0.16),
              (0.62, 0.84, 0.26, 0.14)]
    for fx, fy, fw, fh in blocks:
        d.rectangle([x0 + w * fx, y0 + h * fy,
                     x0 + w * (fx + fw), y0 + h * (fy + fh)],
                    fill=(140, 130, 115))
    cx = x0 + w * 0.45
    d.arc([cx - 9, y1 - 16, cx + 9, y1 - 2], 180, 360,
          fill=(250, 200, 60), width=3)


def art_school(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(235, 225, 200))
    w, h = x1 - x0, y1 - y0
    d.polygon([(x0 + w * 0.06, y0 + h * 0.42), (x0 + w * 0.5, y0 + h * 0.10),
               (x1 - w * 0.06, y0 + h * 0.42)], fill=(140, 28, 28))
    d.rectangle([x0 + w * 0.08, y0 + h * 0.42, x1 - w * 0.08, y1 - 2],
                fill=(150, 120, 90))
    for i in range(3):
        for j in range(2):
            wx0 = x0 + w * (0.16 + i * 0.24)
            wy0 = y0 + h * (0.52 + j * 0.20)
            d.rectangle([wx0, wy0, wx0 + w * 0.12, wy0 + h * 0.10],
                        fill=(255, 250, 200))
    d.rectangle([x0 + w * 0.46, y1 - h * 0.22, x0 + w * 0.54, y1 - 2],
                fill=(60, 45, 30))


def art_barrel(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(225, 220, 205))
    w, h = x1 - x0, y1 - y0
    cx = x0 + w * 0.42
    bw = min(w * 0.24, 40)
    d.rectangle([cx - bw / 2, y0 + h * 0.22, cx + bw / 2, y1 - h * 0.12],
                fill=(110, 90, 60))
    d.ellipse([cx - bw / 2, y0 + h * 0.10, cx + bw / 2, y0 + h * 0.30],
              fill=(140, 115, 75))
    d.ellipse([cx - bw / 2, y1 - h * 0.24, cx + bw / 2, y1 - h * 0.04],
              fill=(80, 65, 40))
    for i in range(2):
        yy = y0 + h * (0.42 + i * 0.20)
        d.line([(cx - bw / 2, yy + 4), (cx + bw / 2, yy)],
               fill=(250, 200, 60), width=3)
    d.rectangle([x1 - w * 0.16, y0 + h * 0.12, x1 - w * 0.04, y0 + h * 0.42],
                fill=(172, 28, 28))
    d.text((x1 - w * 0.115, y0 + h * 0.14), "!", font=F_TAG,
           fill=(255, 255, 255))


def art_jewel(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(230, 225, 245))
    w, h = x1 - x0, y1 - y0
    cx, cy = x0 + w / 2, y0 + h / 2
    gw, gh = w * 0.20, h * 0.36
    d.polygon([(cx - gw, cy - gh * 0.3), (cx - gw * 0.55, cy - gh),
               (cx + gw * 0.55, cy - gh), (cx + gw, cy - gh * 0.3),
               (cx, cy + gh)], fill=(140, 190, 230))
    d.line([(cx - gw, cy - gh * 0.3), (cx + gw, cy - gh * 0.3)],
           fill=(255, 255, 255), width=1)
    d.line([(cx, cy - gh), (cx, cy + gh)], fill=(255, 255, 255), width=1)
    for sx, sy in [(x0 + w * 0.08, y0 + h * 0.20),
                   (x1 - w * 0.08, y0 + h * 0.24)]:
        d.line([(sx - 3, sy), (sx + 3, sy)], fill=(255, 255, 255), width=1)
        d.line([(sx, sy - 3), (sx, sy + 3)], fill=(255, 255, 255), width=1)


def art_protest(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(240, 235, 220))
    w, h = x1 - x0, y1 - y0
    cols = [(172, 28, 28), (28, 64, 120), (36, 110, 66)]
    for i, c in enumerate(cols):
        px = x0 + w * (0.12 + i * 0.30)
        pw = w * 0.18
        d.rectangle([px, y0 + h * 0.14, px + pw, y0 + h * 0.52], fill=c)
        d.line([(px + pw / 2, y0 + h * 0.52), (px + pw / 2, y1 - h * 0.10)],
               fill=(90, 80, 65), width=2)
        d.line([(px + 2, y0 + h * 0.33), (px + pw - 2, y0 + h * 0.33)],
               fill=(255, 255, 255), width=1)
    for i in range(5):
        hx = x0 + w * (0.10 + i * 0.20)
        d.ellipse([hx - 2.5, y1 - h * 0.14, hx + 2.5, y1 - h * 0.04],
                  fill=(74, 66, 54))


def art_dove(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(200, 220, 240))
    w, h = x1 - x0, y1 - y0
    cx, cy = x0 + w * 0.46, y0 + h * 0.55
    d.ellipse([cx - w * 0.14, cy - h * 0.18, cx + w * 0.10, cy + h * 0.22],
              fill=(255, 255, 255))
    d.ellipse([cx + w * 0.04, cy - h * 0.38, cx + w * 0.15, cy - h * 0.06],
              fill=(255, 255, 255))
    d.polygon([(cx - w * 0.02, cy - h * 0.30), (cx + w * 0.10, cy - h * 0.42),
               (cx + w * 0.06, cy - h * 0.10)], fill=(240, 240, 240))
    d.ellipse([cx + w * 0.115, cy - h * 0.32, cx + w * 0.135, cy - h * 0.26],
              fill=(28, 24, 19))
    d.polygon([(cx + w * 0.15, cy - h * 0.30), (cx + w * 0.19, cy - h * 0.26),
               (cx + w * 0.15, cy - h * 0.22)], fill=(220, 150, 60))
    d.line([(x0 + w * 0.06, y1 - h * 0.10), (x0 + w * 0.16, y1 - h * 0.22)],
           fill=(60, 120, 60), width=2)


def art_ai(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(30, 40, 60))
    w, h = x1 - x0, y1 - y0
    cx, cy = x0 + w / 2, y0 + h / 2
    nodes = [(x0 + w * 0.08, y0 + h * 0.16), (x1 - w * 0.08, y0 + h * 0.16),
             (x0 + w * 0.08, y1 - h * 0.16), (x1 - w * 0.08, y1 - h * 0.16),
             (cx - w * 0.12, cy - h * 0.22), (cx + w * 0.12, cy + h * 0.22)]
    for nx, ny in nodes:
        d.line([(cx, cy), (nx, ny)], fill=(80, 140, 180), width=1)
    s = min(w, h) * 0.16
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(90, 200, 220))
    d.rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2],
                fill=(30, 40, 60))
    for nx, ny in nodes:
        d.ellipse([nx - 2.5, ny - 2.5, nx + 2.5, ny + 2.5],
                  fill=(250, 180, 80))


def art_flood(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(200, 225, 240))
    w, h = x1 - x0, y1 - y0
    d.polygon([(x0 + w * 0.08, y0 + h * 0.55), (x0 + w * 0.5, y0 + h * 0.18),
               (x1 - w * 0.08, y0 + h * 0.55)], fill=(140, 28, 28))
    d.rectangle([x0 + w * 0.12, y0 + h * 0.55, x1 - w * 0.12, y0 + h * 0.72],
                fill=(200, 180, 150))
    for i in range(2):
        yy = y0 + h * (0.74 + i * 0.12)
        for k in range(3):
            ax0 = x0 + w * (0.06 + k * 0.30) + i * 4
            d.arc([ax0, yy, ax0 + w * 0.16, yy + h * 0.12], 180, 360,
                  fill=(28, 90, 150), width=2)


ART = {
    "nato": art_nato, "chart": art_chart, "cricket": art_cricket,
    "quake": art_quake, "health": art_health, "mountain": art_mountain,
    "football": art_football, "rescue": art_rescue, "school": art_school,
    "barrel": art_barrel, "jewel": art_jewel, "protest": art_protest,
    "dove": art_dove, "ai": art_ai, "flood": art_flood,
}

# ---------------------------------------------------------------- map
# Equirectangular projection over lon -170..180, lat -58..84. The
# coarse coastline polygons miss a few small coastal strips where
# story dots sit (San Francisco, Mayon, Selangor, Tokyo, Wellington),
# so small land patches cover exactly those dots. Story 4 (Vanuatu
# quake) is a true sea location and is whitelisted as such.

PATCHES = [
    [(-123.4, 38.8), (-122.0, 38.8), (-121.9, 36.9), (-122.9, 36.9)],
    [(122.0, 14.1), (124.3, 14.1), (124.0, 12.9), (122.2, 12.9)],
    [(100.6, 5.9), (102.0, 5.9), (102.8, 3.2), (102.4, 1.7),
     (100.9, 1.9), (100.5, 4.0)],
    [(138.8, 34.9), (140.4, 34.9), (140.4, 36.9), (138.8, 36.9)],
    [(173.5, -40.7), (175.7, -40.7), (175.2, -41.9), (173.7, -41.9)],
    # Italy: the coarse Eurasia loop skips the boot, so Rome reads as sea.
    [(7, 43.8), (12.5, 44.2), (15, 42.5), (16.5, 41.5), (18, 40.5),
     (15.5, 40.2), (13.5, 41.0), (12, 41.5), (10, 42.5), (8, 43.5)],
    # Benghazi coast: the Africa loop cuts the corner at lon 20.
    [(18.8, 32.6), (21.2, 32.6), (21.2, 31.8), (18.8, 31.8)],
]

SEA_STORIES = {4}

MAP_LON = (-170.0, 180.0)
MAP_LAT = (-58.0, 84.0)


def _project(x0, y0, x1, y1, lon, lat):
    s = min((x1 - x0) / (MAP_LON[1] - MAP_LON[0]),
            (y1 - y0) / (MAP_LAT[1] - MAP_LAT[0]))
    w_used = (MAP_LON[1] - MAP_LON[0]) * s
    h_used = (MAP_LAT[1] - MAP_LAT[0]) * s
    ox = x0 + (x1 - x0 - w_used) / 2
    oy = y0 + (y1 - y0 - h_used) / 2
    return ox + (lon - MAP_LON[0]) * s, oy + (MAP_LAT[1] - lat) * s


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xint = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xint:
                inside = not inside
        j = i
    return inside


def _on_land(lon, lat):
    for poly in LAND_POLYS + PATCHES:
        if _in_poly(lon, lat, poly):
            for sea in SEA_POLYS:
                if _in_poly(lon, lat, sea):
                    return False
            return True
    return False


def check_dots():
    """Every story dot must sit on land, except whitelisted sea stories."""
    bad = []
    for (n, r, la, lo, *_) in ALL_STORIES:
        if n in SEA_STORIES:
            continue
        if not _on_land(lo, la):
            bad.append(n)
    return bad


def _solve_badges(dots, x0, y0, x1, y1):
    """Place each badge so it stays inside the map box, never overlaps
    another badge, and never covers a dot. Tries the hand-tuned offset
    first, then rings of increasing radius. Most-constrained dots go
    first so the dense Europe / East Asia clusters pack cleanly."""
    order = sorted(dots, key=lambda n: (
        -sum(1 for m, (qx, qy) in dots.items()
             if m != n and abs(qx - dots[n][0]) < 30
             and abs(qy - dots[n][1]) < 30), n))
    rings = []
    for r in (14, 20, 26, 32, 40, 48, 56):
        for ang in range(0, 360, 30):
            rings.append((round(r * math.cos(math.radians(ang))),
                          round(r * math.sin(math.radians(ang)))))
    placed = {}
    boxes = []
    for n in order:
        px, py = dots[n]
        cands = [BADGE_OFF.get(n, (16, -14))] + rings
        chosen = None
        for ox, oy in cands:
            bx, by = px + ox, py + oy
            if bx - 7 < x0 or by - 7 < y0 or bx + 7 > x1 or by + 7 > y1:
                continue
            if any(bx - 7 < b[2] and b[0] < bx + 7 and
                   by - 7 < b[3] and b[1] < by + 7 for b in boxes):
                continue
            if any(m != n and bx - 10 <= qx <= bx + 10 and
                   by - 10 <= qy <= by + 10
                   for m, (qx, qy) in dots.items()):
                continue
            chosen = (bx, by)
            break
        if chosen is None:
            chosen = (px + 16, py - 14)
        placed[n] = chosen
        boxes.append((chosen[0] - 7, chosen[1] - 7,
                      chosen[0] + 7, chosen[1] + 7))
    return placed


def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=SEA)
    for lon in range(-150, 181, 30):
        gx, _ = _project(x0, y0, x1, y1, lon, 0)
        _, gy0 = _project(x0, y0, x1, y1, 0, MAP_LAT[1])
        _, gy1 = _project(x0, y0, x1, y1, 0, MAP_LAT[0])
        d.line([(gx, gy0), (gx, gy1)], fill=GRID, width=1)
    for lat in range(-30, 61, 30):
        _, gy = _project(x0, y0, x1, y1, 0, lat)
        gx0, _ = _project(x0, y0, x1, y1, MAP_LON[0], 0)
        gx1, _ = _project(x0, y0, x1, y1, MAP_LON[1], 0)
        d.line([(gx0, gy), (gx1, gy)], fill=GRID, width=1)
    for poly in LAND_POLYS:
        pts = [_project(x0, y0, x1, y1, lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND)
        d.line(pts + [pts[0]], fill=LAND_EDGE, width=1)
    for poly in SEA_POLYS:
        pts = [_project(x0, y0, x1, y1, lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=SEA)
    for poly in PATCHES:
        pts = [_project(x0, y0, x1, y1, lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND)
    dots = {}
    for (n, r, la, lo, *_) in ALL_STORIES:
        px, py = _project(x0, y0, x1, y1, lo, la)
        dots[n] = (px, py)
    badges = _solve_badges(dots, x0, y0, x1, y1)
    for n, (px, py) in dots.items():
        bx, by = badges[n]
        d.line([(px, py), (bx, by)], fill=(110, 20, 20), width=3)
        d.line([(px, py), (bx, by)], fill=(255, 255, 255), width=1)
    for n, (px, py) in dots.items():
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 255))
        d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=RED)
    for n, (px, py) in dots.items():
        bx, by = badges[n]
        d.ellipse([bx - 6.5, by - 6.5, bx + 6.5, by + 6.5],
                  fill=RED, outline=(255, 255, 255))
        w = d.textlength(str(n), font=F_BADGE)
        d.text((bx - w / 2, by - 5), str(n), font=F_BADGE,
               fill=(255, 255, 255))
    return dots, badges


def check_badges(badges, dots, x0, y0, x1, y1):
    """Badge boxes must not overlap each other, cover another story's
    dot, or leave the map box. `badges` maps story number to the
    placed badge centre (as drawn by draw_map)."""
    boxes = {}
    for n, (bx, by) in badges.items():
        boxes[n] = (bx - 7, by - 7, bx + 7, by + 7)
    problems = []
    ns = sorted(boxes)
    for i in range(len(ns)):
        for j in range(i + 1, len(ns)):
            a, b = boxes[ns[i]], boxes[ns[j]]
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                problems.append((ns[i], ns[j], "overlap"))
    for n, (bx0, by0, bx1, by1) in boxes.items():
        if bx0 < x0 or by0 < y0 or bx1 > x1 or by1 > y1:
            problems.append((n, "outside"))
    for n, (bx0, by0, bx1, by1) in boxes.items():
        for m, (px, py) in dots.items():
            if m != n and bx0 - 2 <= px <= bx1 + 2 and by0 - 2 <= py <= by1 + 2:
                problems.append((n, "covers-dot", m))
    return problems

# ---------------------------------------------------------------- layout

from PIL import ImageFilter


def wrap_max(d, text, fnt, width, max_lines):
    lines = wrap(d, text, fnt, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + "…", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        if lines:
            lines[-1] = lines[-1].rstrip() + "…"
    return lines


def draw_masthead(d):
    text_center(d, W / 2, 8, "THE WORLD TODAY", F_MAST, INK)
    text_center(d, W / 2, 60,
                "MONDAY, 23 NOVEMBER 2026  ·  ONE PAGE  ·  39 STORIES  ·  "
                "EVERY DATE VERIFIED", F_DATE, INK_SOFT)
    rule(d, 16, W - 16, 76, fill=INK, width=2)
    rule(d, 16, W - 16, 79, fill=RULE, width=1)
    return 84


def draw_stats(d, y):
    cw = (W - 32) / 6
    for i, (num, lab) in enumerate(STATS):
        cx = 16 + cw * i + cw / 2
        text_center(d, cx, y, num, F_STAT_N, RED_DARK)
        text_center(d, cx, y + 20, lab, F_STAT_L, INK_SOFT)
        if i:
            d.line([(16 + cw * i, y + 2), (16 + cw * i, y + 30)],
                   fill=RULE, width=1)
    rule(d, 16, W - 16, y + 34, fill=RULE, width=1)
    return y + 40


HERO_ART_H = 40


def draw_heroes(d, y):
    xs = [16, 344, 672]
    bottom = y
    for (n, region, la, lo, kicker, head, text, tag, art), x in zip(HEROES, xs):
        yy = y
        d.text((x, yy), kicker, font=F_KICK, fill=RED)
        yy += 13
        for ln in wrap_max(d, head, F_HERO_H, 320, 3):
            d.text((x, yy), ln, font=F_HERO_H, fill=INK)
            yy += 19
        yy += 4
        ART[art](d, x, yy, x + 320, yy + HERO_ART_H)
        d.rectangle([x, yy, x + 320, yy + HERO_ART_H], outline=RULE, width=1)
        yy += HERO_ART_H + 6
        for ln in wrap_max(d, text, F_HERO_T, 320, 4):
            d.text((x, yy), ln, font=F_HERO_T, fill=INK)
            yy += 13
        yy += 4
        d.text((x, yy), tag, font=F_TAG, fill=RED_DARK)
        yy += 11
        bottom = max(bottom, yy)
    rule(d, 16, W - 16, bottom + 2, fill=RULE, width=1)
    return bottom + 8


MID_ROWS = [(4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15, 16)]
MID_ART_H = 20


def draw_mids(d, y):
    mid_by_n = {m[0]: m for m in MIDS}
    yy = y
    for row in MID_ROWS:
        ncols = len(row)
        cw = (992 - (ncols - 1) * 8) / ncols
        cards = []
        row_h = 0
        for n in row:
            (_, region, la, lo, head, text, tag, art) = mid_by_n[n]
            hl = wrap_max(d, head, F_MID_H, cw - 8, 2)
            tl = wrap_max(d, text, F_MID_T, cw - 8, 3)
            h = 4 + MID_ART_H + 3 + len(hl) * 14 + 2 + len(tl) * 11 + 3 + 10 + 4
            cards.append((n, hl, tl, h))
            row_h = max(row_h, h)
        for i, (n, hl, tl, h) in enumerate(cards):
            (_, region, la, lo, head, text, tag, art) = mid_by_n[n]
            x = 16 + i * (cw + 8)
            d.rectangle([x, yy, x + cw, yy + row_h],
                        fill=(252, 249, 240), outline=RULE, width=1)
            ART[art](d, x + 3, yy + 4, x + cw - 3, yy + 4 + MID_ART_H)
            cy = yy + 4 + MID_ART_H + 3
            for ln in hl:
                d.text((x + 4, cy), ln, font=F_MID_H, fill=INK)
                cy += 14
            cy += 2
            for ln in tl:
                d.text((x + 4, cy), ln, font=F_MID_T, fill=INK_SOFT)
                cy += 11
            d.text((x + 4, yy + row_h - 13), tag, font=F_TAG, fill=RED_DARK)
        yy += row_h + 4
    return yy


def draw_briefs(d, x0, y0, w):
    d.text((x0, y0), "THE DAY IN BRIEF", font=F_REGION, fill=RED_DARK)
    rule(d, x0, x0 + w, y0 + 14, fill=RULE, width=1)
    col_w = (w - 12) / 2
    cols = [BRIEFS[:12], BRIEFS[12:]]
    yy0 = y0 + 20
    max_bottom = yy0
    for ci, col in enumerate(cols):
        x = x0 + ci * (col_w + 12)
        yy = yy0
        for (n, region, la, lo, text) in col:
            num = str(n)
            nw = d.textlength(num + "  ", font=F_BRIEF_N)
            lines = wrap(d, text, F_BRIEF, col_w - nw)
            d.text((x, yy), num, font=F_BRIEF_N, fill=RED_DARK)
            ly = yy
            for ln in lines:
                d.text((x + nw, ly), ln, font=F_BRIEF, fill=INK)
                ly += 12
            yy = ly
        max_bottom = max(max_bottom, yy)
    return max_bottom


def draw_datecheck(d, x0, y0, w):
    col_w = (w - 16 - 12) / 2
    cols = [DATE_CHECK[:4], DATE_CHECK[4:]]
    wrapped = []
    content_h = 0
    for col in cols:
        rows = []
        for event, date in col:
            rows.append(wrap(d, event + " — " + date, F_NOTE, col_w))
        wrapped.append(rows)
        content_h = max(content_h, sum(len(r) * 12 + 2 for r in rows))
    box_h = 5 + 15 + content_h + 5
    d.rectangle([x0, y0, x0 + w, y0 + box_h], outline=RED, width=2)
    d.text((x0 + 8, y0 + 5), "DATE CHECK — THESE HAPPENED ON OTHER DAYS",
           font=F_DC_B, fill=RED)
    for ci, rows in enumerate(wrapped):
        x = x0 + 8 + ci * (col_w + 12)
        yy = y0 + 22
        for lines in rows:
            for ln in lines:
                d.text((x, yy), ln, font=F_NOTE, fill=INK)
                yy += 12
            yy += 2
    return y0 + box_h


def draw_bottom(d, y0):
    d.text((516, y0), "WHERE IT HAPPENED — EVERY STORY PINNED",
           font=F_REGION, fill=RED_DARK)
    map_y0 = y0 + 18
    map_y1 = map_y0 + 190
    dots, badges = draw_map(d, 516, map_y0, 1008, map_y1)
    d.text((516, map_y1 + 4),
           "ALL DOTS AT TRUE LOCATIONS · 4 = QUAKE AT SEA OFF VANUATU",
           font=F_FOOT, fill=INK_SOFT)
    dc_y0 = map_y1 + 18
    dc_end = draw_datecheck(d, 516, dc_y0, 492)
    briefs_end = draw_briefs(d, 16, y0, 484)
    return max(briefs_end, dc_end), dots, badges, (516, map_y0, 1008, map_y1)


def draw_regions(d, y):
    total = sum(c for _, c, _ in REGIONS)
    x = 16
    for name, count, color in REGIONS:
        wseg = 992 * count / total
        d.rectangle([x, y, x + wseg, y + 12], fill=color)
        x += wseg
    parts = "   ·   ".join("%s %d" % (name, count)
                           for name, count, _ in REGIONS)
    text_center(d, W / 2, y + 16, parts, F_REGION, INK_SOFT)
    text_center(d, W / 2, y + 28,
                "%d STORIES · %d REGIONS · ONE PAGE" % (total, len(REGIONS)),
                F_REGION, INK)
    return y + 42


def draw_footer(d, y):
    text_center(d, W / 2, y,
                "SOURCES: AP · REUTERS · BBC · THE HINDU · IANS · USGS · "
                "FOCUS TAIWAN — ALL STORIES DATED MONDAY 23 NOVEMBER 2026",
                F_FOOT, INK_SOFT)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    paper_texture(d)
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-80, -80, W + 80, H + 80], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGB", (W, H), (214, 202, 172))
    img = Image.composite(img, dark, vig)
    d = ImageDraw.Draw(img)
    y = draw_masthead(d)
    y = draw_stats(d, y + 4)
    heroes_end = draw_heroes(d, y + 6)
    mids_end = draw_mids(d, heroes_end + 6)
    bottom_end, dots, badges, mapbox = draw_bottom(d, mids_end + 8)
    draw_regions(d, 972)
    draw_footer(d, 1010)
    img.save(OUT, optimize=True)
    return heroes_end, mids_end, bottom_end, dots, badges, mapbox


if __name__ == "__main__":
    heroes_end, mids_end, bottom_end, dots, badges, mapbox = render()
    data = open(OUT, "rb").read()
    print("entry.png bytes:", len(data))
    print("entry.png md5:", hashlib.md5(data).hexdigest())
    print("stories:", len(ALL_STORIES),
          "regions sum:", sum(c for _, c, _ in REGIONS))
    print("heroes end y:", heroes_end, "mids end y:", mids_end,
          "bottom end y:", bottom_end)
    print("dots off land:", check_dots())
    print("badge problems:", check_badges(badges, dots, *mapbox))
    offs = [round(math.hypot(badges[n][0] - dots[n][0],
                              badges[n][1] - dots[n][1]))
            for n in dots]
    print("badge offsets: max", max(offs), "px, mean",
          round(sum(offs) / len(offs), 1), "px")
