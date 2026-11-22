# 22 November 2026 front page. Stdlib only. Draws every pixel itself:
# no image file, no network, no font file. Deterministic output.
import os
import struct
import zlib
from binascii import crc32

W = 1024
H = 1024

CREAM = (247, 243, 232)
PAPER = (255, 253, 246)
INK = (17, 17, 17)
GREY = (90, 88, 80)
RED = (185, 28, 28)
BLUE = (29, 78, 216)
TEAL = (13, 116, 110)
GOLD = (180, 130, 20)
GREEN = (22, 120, 70)
PURPLE = (110, 60, 170)
SEA = (140, 175, 200)
LAND = (232, 222, 190)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (220, 100, 20)
SKY = (190, 215, 235)

# 5x7 bitmap glyphs, one row per string. Written for this entry.
GLYPHS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "(": ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
    ")": ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
    "%": ["##..#", "#.#.#", "...#.", "..#..", ".#...", "#.#.#", "#..##"],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "&": [".###.", "#...#", "#...#", ".##..", "#.#.#", "#..#.", ".##.#"],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ";": [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    "*": [".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    "$": ["..#..", ".####", "#.#..", ".###.", "...#.", "####.", "..#.."],
    "•": [".....", ".....", ".###.", ".###.", ".###.", ".....", "....."],
    "—": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
}

BUF = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i], BUF[i + 1], BUF[i + 2] = c


def rect(x, y, w, h, c):
    for yy in range(max(0, y), min(H, y + h)):
        base = (yy * W + max(0, x)) * 3
        for xx in range(max(0, x), min(W, x + w)):
            i = (yy * W + xx) * 3
            BUF[i], BUF[i + 1], BUF[i + 2] = c


def border(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
        for xx in range(cx - dx, cx + dx + 1):
            px(xx, yy, c)


def ring(cx, cy, r, c, t=2):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
            if r - t < d <= r:
                px(xx, yy, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        if t <= 1:
            px(x, y, c)
        else:
            circle(x, y, t // 2, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def poly(points, c):
    # filled polygon by scanline
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                px(x, y, c)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = GLYPHS.get(ch, GLYPHS["?"])
        for row in range(7):
            for col in range(5):
                if g[row][col] == "#":
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def wrap(s, scale, maxw):
    words = s.upper().split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_width(trial, scale) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, maxw, c, lh=None):
    if lh is None:
        lh = 8 * scale + 2
    yy = y
    for ln in wrap(s, scale, maxw):
        draw_text(x, yy, ln, scale, c)
        yy += lh
    return yy


def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    return out + struct.pack(">I", crc32(tag + data) & 0xFFFFFFFF)


def write_png(path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += BUF[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---- pictograms: small flat scenes drawn with rects, circles and lines ----

def icon_summit(x, y, w, h):
    rect(x, y, w, h, SKY)
    # three flag panels: US, China, Russia
    fw = w // 3
    rect(x, y + 8, fw - 6, h - 40, WHITE)
    for i in range(4):
        rect(x, y + 10 + i * 9, fw - 6, 4, RED)
    rect(x + 4, y + 12, 22, 16, BLUE)
    rect(x + fw, y + 8, fw - 6, h - 40, RED)
    circle(x + fw + (fw - 6) // 2, y + (h - 40) // 2 + 4, 7, GOLD)
    rect(x + 2 * fw, y + 8, fw - 6, h - 40, WHITE)
    rect(x + 2 * fw, y + 8, fw - 6, (h - 40) // 3, WHITE)
    rect(x + 2 * fw, y + 8 + (h - 40) // 3, fw - 6, (h - 40) // 3, BLUE)
    rect(x + 2 * fw, y + 8 + 2 * (h - 40) // 3, fw - 6, (h - 40) // 3 + 2, RED)
    # table line
    hline(x + 6, y + h - 22, w - 12, INK, 3)
    circle(x + w // 2 - 34, y + h - 30, 8, INK)
    circle(x + w // 2, y + h - 30, 8, INK)
    circle(x + w // 2 + 34, y + h - 30, 8, INK)


def icon_climate(x, y, w, h):
    rect(x, y, w, h, (220, 235, 220))
    circle(x + w // 2, y + 26, 18, GOLD)
    # factory
    rect(x + 14, y + h - 44, 34, 30, GREY)
    rect(x + 52, y + h - 56, 30, 42, GREY)
    rect(x + 20, y + h - 58, 8, 16, GREY)
    circle(x + 30, y + h - 62, 6, (200, 200, 200))
    circle(x + 42, y + h - 68, 8, (210, 210, 210))
    # thermometer
    rect(x + w - 30, y + 12, 8, h - 40, WHITE)
    circle(x + w - 26, y + h - 24, 10, RED)
    rect(x + w - 28, y + 20, 4, h - 52, RED)
    # leaf
    poly([(x + w // 2 - 8, y + h - 14), (x + w // 2 + 16, y + h - 14),
          (x + w // 2 + 8, y + h - 4), (x + w // 2 - 16, y + h - 4)], GREEN)


def icon_market(x, y, w, h):
    rect(x, y, w, h, (250, 235, 235))
    # axes
    vline(x + 12, y + 10, h - 26, INK, 2)
    hline(x + 12, y + h - 16, w - 24, INK, 2)
    # falling line
    line(x + 18, y + 18, x + w // 3, y + 30, RED, 3)
    line(x + w // 3, y + 30, x + 2 * w // 3, y + 26, RED, 3)
    line(x + 2 * w // 3, y + 26, x + w - 16, y + h - 24, RED, 3)
    # down arrow
    poly([(x + w - 26, y + h - 34), (x + w - 10, y + h - 34), (x + w - 18, y + h - 18)], RED)
    draw_text(x + 18, y + 6, "-3.7%", 1, RED)


def icon_badge(x, y, w, h):
    rect(x, y, w, h, (235, 235, 250))
    # star badge
    cx, cy = x + w // 2, y + h // 2 - 6
    poly([(cx, cy - 26), (cx + 8, cy - 8), (cx + 26, cy - 6), (cx + 11, cy + 7),
          (cx + 17, cy + 26), (cx, cy + 14), (cx - 17, cy + 26), (cx - 11, cy + 7),
          (cx - 26, cy - 6), (cx - 8, cy - 8)], GOLD)
    circle(cx, cy, 12, BLUE)
    circle(cx, cy, 5, WHITE)
    # bars
    vline(x + 16, y + 12, h - 24, INK, 3)
    vline(x + 26, y + 12, h - 24, INK, 3)
    vline(x + w - 28, y + 12, h - 24, INK, 3)
    vline(x + w - 18, y + 12, h - 24, INK, 3)


def icon_missile(x, y, w, h):
    rect(x, y, w, h, (230, 230, 235))
    # building hit
    rect(x + 14, y + h - 40, 30, 28, GREY)
    rect(x + w - 44, y + h - 52, 30, 40, GREY)
    # missile diagonal
    line(x + w - 20, y + 10, x + 34, y + h - 44, INK, 4)
    poly([(x + w - 20, y + 10), (x + w - 34, y + 16), (x + w - 26, y + 26)], RED)
    # blast star
    cx, cy = x + 40, y + h - 48
    poly([(cx, cy - 16), (cx + 5, cy - 5), (cx + 16, cy), (cx + 5, cy + 5),
          (cx, cy + 16), (cx - 5, cy + 5), (cx - 16, cy), (cx - 5, cy - 5)], ORANGE)
    circle(cx, cy, 5, GOLD)


def icon_quake(x, y, w, h):
    rect(x, y, w, h, (225, 235, 245))
    # mountains
    poly([(x + 6, y + h - 14), (x + w // 3, y + 12), (x + 2 * w // 3 - 10, y + h - 14)], (120, 130, 140))
    poly([(x + w // 3, y + h - 14), (x + 2 * w // 3, y + 20), (x + w - 6, y + h - 14)], (150, 155, 160))
    circle(x + w // 3, y + 16, 5, WHITE)
    # shaking building + crack
    rect(x + w - 44, y + h - 44, 30, 30, INK)
    line(x + w - 44, y + h - 44, x + w - 30, y + h - 30, RED, 2)
    line(x + w - 30, y + h - 30, x + w - 38, y + h - 16, RED, 2)
    line(x + 12, y + 12, x + 26, y + 26, RED, 2)
    line(x + 26, y + 26, x + 16, y + 40, RED, 2)


def icon_scales(x, y, w, h):
    rect(x, y, w, h, (240, 235, 220))
    cx, cy = x + w // 2, y + 16
    vline(cx, y + 12, h - 36, INK, 3)
    hline(cx - 34, y + 18, 68, INK, 3)
    # pans
    poly([(cx - 44, y + 34), (cx - 24, y + 34), (cx - 34, y + 50)], GOLD)
    poly([(cx + 24, y + 34), (cx + 44, y + 34), (cx + 34, y + 50)], GOLD)
    line(cx - 34, y + 20, cx - 44, y + 34, INK, 2)
    line(cx - 34, y + 20, cx - 24, y + 34, INK, 2)
    line(cx + 34, y + 20, cx + 24, y + 34, INK, 2)
    line(cx + 34, y + 20, cx + 44, y + 34, INK, 2)
    rect(cx - 22, y + h - 22, 44, 8, INK)


def icon_tanker(x, y, w, h):
    rect(x, y, w, h, SEA)
    # hull
    poly([(x + 12, y + h - 34), (x + w - 12, y + h - 34), (x + w - 26, y + h - 14), (x + 26, y + h - 14)], RED)
    rect(x + w - 44, y + h - 58, 22, 24, WHITE)
    rect(x + 20, y + h - 46, 10, 12, INK)
    # flame
    circle(x + w // 2, y + 22, 9, ORANGE)
    circle(x + w // 2 - 10, y + 28, 7, GOLD)
    # waves
    hline(x + 6, y + h - 8, w - 12, WHITE, 3)


def icon_border(x, y, w, h):
    rect(x, y, w, h, (235, 240, 235))
    # Estonian flag
    rect(x + 12, y + 10, 44, 10, BLUE)
    rect(x + 12, y + 20, 44, 10, BLACK)
    rect(x + 12, y + 30, 44, 10, WHITE)
    # barrier stripes
    for i in range(5):
        rect(x + 60 + i * 20, y + 12, 12, 34, RED if i % 2 == 0 else WHITE)
    rect(x + 56, y + 12, 4, h - 26, INK)
    rect(x + w - 22, y + 12, 4, h - 26, INK)
    hline(x + 12, y + h - 18, w - 24, INK, 3)
    draw_text(x + 14, y + h - 14, "1 DEC", 1, INK)


def icon_trade(x, y, w, h):
    rect(x, y, w, h, (235, 240, 250))
    # two arrows meeting
    line(x + 12, y + 24, x + w // 2 - 8, y + 24, BLUE, 4)
    poly([(x + w // 2 - 8, y + 24), (x + w // 2 - 22, y + 16), (x + w // 2 - 22, y + 32)], BLUE)
    line(x + w - 12, y + h - 26, x + w // 2 + 8, y + h - 26, RED, 4)
    poly([(x + w // 2 + 8, y + h - 26), (x + w // 2 + 22, y + h - 34), (x + w // 2 + 22, y + h - 18)], RED)
    circle(x + w // 2, y + h // 2, 16, GOLD)
    draw_text(x + w // 2 - 12, y + h // 2 - 7, "98%", 1, INK)
    # crates
    rect(x + 14, y + h - 26, 20, 14, (170, 120, 70))
    rect(x + w - 34, y + 10, 20, 14, (170, 120, 70))


def icon_boat(x, y, w, h):
    rect(x, y, w, h, SEA)
    # capsized hull
    poly([(x + 16, y + h - 30), (x + w - 16, y + h - 30), (x + w - 30, y + h - 48), (x + 30, y + h - 48)], (90, 60, 40))
    # waves
    for yy in (y + h - 12, y + h - 22):
        for xx in range(x + 6, x + w - 6, 18):
            line(xx, yy, xx + 8, yy - 5, WHITE, 2)
    circle(x + w // 2, y + 18, 8, ORANGE)
    draw_text(x + w // 2 - 6, y + 11, "24", 1, WHITE)


ICONS = {
    "summit": icon_summit, "climate": icon_climate, "market": icon_market,
    "badge": icon_badge, "missile": icon_missile, "quake": icon_quake,
    "scales": icon_scales, "tanker": icon_tanker, "border": icon_border,
    "trade": icon_trade, "boat": icon_boat,
}


def panel(x, y, w, h, num, kicker, kcolor, headline, deck, icon):
    rect(x, y, w, h, PAPER)
    border(x, y, w, h, INK, 2)
    # number badge
    circle(x + 18, y + 16, 12, RED)
    draw_text(x + 18 - (6 if num < 10 else 11), y + 9, str(num), 1, WHITE)
    draw_text(x + 34, y + 9, kicker, 1, kcolor)
    # icon band
    iy = y + 30
    ih = 80 if h >= 200 else 68
    ICONS[icon](x + 8, iy, w - 16, ih)
    border(x + 8, iy, w - 16, ih, GREY, 1)
    ty = iy + ih + 8
    hscale = 2 if w < 300 else 3
    ty = draw_para(x + 10, ty, headline, hscale, w - 20, INK)
    draw_para(x + 10, ty + 2, deck, 1, w - 20, GREY)

# ---- page layout ----

def masthead():
    rect(0, 0, W, 104, CREAM)
    hline(0, 102, W, INK, 3)
    draw_text(16, 12, "THE WORLD TODAY", 4, INK)
    draw_text(16, 52, "ONE DAY'S WORLD NEWS, IN ONE IMAGE", 2, RED)
    draw_text(723, 12, "22 NOVEMBER 2026", 3, INK)
    draw_text(723, 42, "SUNDAY  •  27 STORIES", 1, GREY)
    hline(16, 72, 992, INK, 2)
    # ticker band
    rect(0, 78, W, 24, RED)
    draw_text(16, 86, "COP31 OVERTIME  •  SHENZHEN SUMMIT  •  CARTEL BOSS HELD  •  MARKETS FALL", 1, WHITE)


def briefs_section(x, y, w, h):
    rect(x, y, w, h, PAPER)
    border(x, y, w, h, INK, 2)
    rect(x, y, w, 22, INK)
    draw_text(x + 10, y + 7, "IN BRIEF: 17 MORE STORIES", 1, WHITE)
    briefs = [
        (11, "BOAT TO FUNERAL CAPSIZES IN NIGERIA: 24 DEAD"),
        (12, "FACTORY FIRE IN BANTEN, INDONESIA: 3 DEAD, DOZENS MISSING"),
        (13, "DENMARK EXPELS RUSSIAN ATTACHE OVER ALLEGED PLOT"),
        (14, "GAZA: ISRAELI STRIKES CONTINUE; AID VEHICLE HIT"),
        (15, "LEBANON'S AOUN BLAMES ISRAEL AND IRAN FOR THREATS"),
        (16, "TRUMP ORDERS CONTRACTORS TO REPORT CONGRESS REQUESTS"),
        (17, "GTA 6: $3.79BN LAUNCH DAY, A RECORD"),
        (18, "AMAZON NEARS $7.5BN DEAL FOR AI STARTUP DECART"),
        (19, "FBI DATABASE BREACH CONFIRMED BY TRUMP (NCIC)"),
        (20, "SEOUL: MINISTER QUITS OVER AI CHEATING SCANDAL"),
        (21, "CRICKET: INDIA 720/9, 352-RUN LEAD OVER NZ"),
        (22, "NEPAL PM BALENDRA SHAH VISITS INDIA, MEETS MODI"),
        (23, "LEEDS STUN CHELSEA 4-1, FIRST WIN THERE SINCE 1999"),
        (24, "RUSSIAN CARGO SHIP HIT BY DRONES, FIRE IN BALTIC SEA"),
        (25, "BASRA POWER PLANT FIRE: 4 KILLED, 35 WOUNDED"),
        (26, "HOUTHIS STRIKE AFTER SAUDI-LED OPERATION IN HODEIDA"),
        (27, "PAOLO BULGARI, JEWELLER WHO BUILT GLOBAL BRAND, DIES AT 89"),
    ]
    colw = w // 2
    for i, (num, txt) in enumerate(briefs):
        col = 0 if i < 9 else 1
        row = i if i < 9 else i - 9
        bx = x + 8 + col * colw
        by = y + 28 + row * 20
        circle(bx + 7, by + 6, 8, BLUE)
        draw_text(bx + 7 - (6 if num < 10 else 11), by - 1, str(num), 1, WHITE)
        draw_para(bx + 20, by - 1, txt, 1, colw - 34, INK, lh=9)


def map_section(x, y, w, h):
    rect(x, y, w, h, PAPER)
    border(x, y, w, h, INK, 2)
    rect(x, y, w, 22, INK)
    draw_text(x + 10, y + 7, "THE WORLD: WHERE IT HAPPENED", 1, WHITE)
    mx, my = x + 8, y + 30
    mw, mh = w - 16, h - 38
    rect(mx, my, mw, mh, SEA)
    # schematic continents
    poly([(mx + 8, my + 18), (mx + 78, my + 10), (mx + 96, my + 34), (mx + 60, my + 52), (mx + 16, my + 48)], LAND)
    poly([(mx + 48, my + 78), (mx + 84, my + 74), (mx + 76, my + 128), (mx + 52, my + 122)], LAND)
    poly([(mx + 132, my + 16), (mx + 176, my + 12), (mx + 182, my + 44), (mx + 146, my + 48)], LAND)
    poly([(mx + 138, my + 56), (mx + 180, my + 54), (mx + 172, my + 112), (mx + 146, my + 108)], LAND)
    poly([(mx + 186, my + 10), (mx + 288, my + 8), (mx + 296, my + 62), (mx + 230, my + 70), (mx + 190, my + 44)], LAND)
    poly([(mx + 252, my + 118), (mx + 292, my + 116), (mx + 288, my + 136), (mx + 256, my + 138)], LAND)
    pins = [
        (1, 252, 40), (2, 184, 44), (3, 44, 32), (4, 30, 52),
        (5, 164, 32), (6, 58, 96), (7, 258, 56), (8, 200, 50),
        (9, 180, 14), (10, 258, 92), (11, 152, 84),
    ]
    for num, px_, py_ in pins:
        circle(mx + px_, my + py_, 9, RED)
        ring(mx + px_, my + py_, 9, WHITE, 2)
        draw_text(mx + px_ - (3 if num < 10 else 6), my + py_ - 3, str(num), 1, WHITE)
    draw_text(mx + 8, my + mh - 12, "SCHEMATIC MAP. NUMBERS MATCH STORIES.", 1, INK)


def footer():
    draw_text(16, 988, "SOURCES: AP, REUTERS, AFP, ONETURN, CNBC, SKY SPORTS. HEADLINES REPORTED 21-22 NOV 2026.", 1, GREY)
    draw_text(16, 1002, "DRAWN FROM REPORTED FACTS ONLY. NO SPECULATION SHOWN AS FACT.", 1, GREY)


def build():
    rect(0, 0, W, H, CREAM)
    masthead()
    # row A: two large panels
    panel(16, 112, 496, 224, 1, "SHENZHEN, CHINA", BLUE,
          "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
          "THREE LEADERS AGREE TO BEGIN TALKS ON CUTTING NUCLEAR RISK.", "summit")
    panel(520, 112, 488, 224, 2, "ANTALYA, TURKEY", GREEN,
          "COP31 TALKS RUN INTO OVERTIME",
          "DRAFT DEAL OMITS 'FOSSIL FUELS'; COUNTRIES SPLIT OVER PHASEOUT.", "climate")
    # row B: four panels
    xs = [16, 262, 508, 754]
    panel(xs[0], 344, 238, 212, 3, "NEW YORK", RED,
          "AI SELL-OFF: US STOCKS FALL INTO CORRECTION",
          "S&P 500 -3.7%; NIKKEI -5.06% AS CHIP SHARES SLIDE.", "market")
    panel(xs[1], 344, 238, 212, 4, "SINALOA, MEXICO", PURPLE,
          "MEXICO CAPTURES CARTEL BOSS 'EL CHAPO ISIDRO'",
          "FAUSTO MEZA FLORES HELD; 11 KILLED IN VIOLENCE AFTER.", "badge")
    panel(xs[2], 344, 238, 212, 5, "UKRAINE / POLAND", RED,
          "MISSILE HITS ZELENSKYY'S HOMETOWN; POLAND HIT TOO",
          "2 KILLED IN KRYVYI RIH; RUSSIAN MISSILES LAND IN POLAND.", "missile")
    panel(xs[3], 344, 238, 212, 6, "JUNIN, PERU", ORANGE,
          "PERU QUAKE: 6.7 SHAKES THE ANDES",
          "1 DEAD, 16 INJURED, 853 DISPLACED IN JUNIN.", "quake")
    # row C: four panels
    panel(xs[0], 564, 238, 192, 7, "THE HAGUE", TEAL,
          "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
          "ICJ RULES ON ROHINGYA; SURVIVORS WELCOME VERDICT.", "scales")
    panel(xs[1], 564, 238, 192, 8, "BAHRAIN / HORMUZ", RED,
          "IRAN STRIKES BAHRAIN SITE; TANKERS HIT",
          "FIRE AT INDUSTRIAL SITE, NO INJURIES; 2 TANKERS HIT.", "tanker")
    panel(xs[2], 564, 238, 192, 9, "TALLINN", BLUE,
          "ESTONIA TO SHUT RUSSIA BORDER",
          "ALL ROAD CROSSINGS CLOSE 1 DEC FOR 6 MONTHS.", "border")
    panel(xs[3], 564, 238, 192, 10, "BRUSSELS", GREEN,
          "EU AND INDONESIA SIGN TRADE DEAL",
          "AFTER 10 YEARS OF TALKS; TARIFFS ON ABOUT 98% TO GO.", "trade")
    # row D: briefs + map
    briefs_section(16, 764, 664, 208)
    map_section(688, 764, 320, 208)
    footer()


def main():
    build()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path)
    print("wrote", path, size, "bytes")


if __name__ == "__main__":
    main()
