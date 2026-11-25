#!/usr/bin/env python3
"""news-image-20261125: one image summing up Wednesday 25 November 2026.

Pure stdlib (zlib + struct only): draws a newspaper front page at 1024x1024
with a tiny built-in 5x7 bitmap font, then writes entry.png. No network, no
timestamps in the output, so two runs write byte-identical files.
"""
import hashlib
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 231)
INK = (22, 22, 22)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
GOLD = (201, 162, 39)
GREY = (110, 104, 92)
SEA1 = (23, 68, 110)
SEA2 = (32, 96, 145)
SEA3 = (66, 135, 178)
SKY = (135, 180, 210)
DUSK1 = (233, 116, 54)
DUSK2 = (242, 163, 82)
TOWER = (40, 32, 48)
WHITE = (255, 255, 255)

# 5x7 bitmap font: '#' is on, '.' is off. Lowercase maps to uppercase.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", "01100", "01100"),
    ",": (".....", ".....", ".....", ".....", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "01110", ".....", ".....", "....."),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", ".....", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", ".....", "00100"),
    "%": ("11001", "11001", "00010", "00100", "01000", "10011", "10011"),
    ":": (".....", "01100", ".....", ".....", ".....", "01100", "....."),
    ";": (".....", "01100", ".....", "01100", "00100", "01000", "....."),
    '"': ("01010", "01010", ".....", ".....", ".....", ".....", "....."),
    "+": (".....", "00100", "00100", "01110", "00100", "00100", "....."),
    "=": (".....", ".....", "01110", ".....", "01110", ".....", "....."),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def circle(self, cx, cy, r, c):
        # filled circle, midpoint style
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if g[row][col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def wrap(self, s, scale, max_w):
        words, lines, cur = s.split(" "), [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if self.text_w(t, scale) <= max_w:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, max_w, lh=None):
        lh = lh or (9 * scale)
        for ln in self.wrap(s, scale, max_w):
            self.text(x, y, ln, scale, c)
            y += lh
        return y


def draw(c):
    c.rect(0, 0, W, H, PAPER)
    # Masthead
    c.rect(0, 0, W, 108, NAVY)
    t = "THE WORLD IN ONE IMAGE"
    c.text((W - c.text_w(t, 4)) // 2, 22, t, 4, WHITE)
    d = "WEDNESDAY 25 NOVEMBER 2026"
    c.text((W - c.text_w(d, 2)) // 2, 72, d, 2, GOLD)
    c.hline(0, 112, W, GOLD, 4)

    # Lead story
    y = 132
    c.text(40, y, "LEAD - UKRAINE WAR", 2, RED)
    y = 158
    y = c.para(40, y, "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA", 3, INK, 944)
    y += 6
    y = c.para(40, y, "Zelenskiy confirms Gulf of Finland strike as Norway urges caution",
               2, GREY, 944)
    # Sea photo: sky, sun, sea bands, ship silhouette
    py, ph = 292, 158
    c.rect(40, py, 944, 52, SKY)
    c.circle(880, py + 26, 20, GOLD)
    c.rect(40, py + 52, 944, 34, SEA3)
    c.rect(40, py + 86, 944, 36, SEA2)
    c.rect(40, py + 122, 944, 36, SEA1)
    c.hline(40, py + 52, 944, WHITE, 2)
    c.hline(40, py + 86, 944, WHITE, 2)
    # ship: hull + funnel + mast
    c.rect(400, py + 96, 260, 22, INK)
    c.rect(430, py + 66, 60, 30, INK)
    c.vline(560, py + 46, 52, INK, 5)
    c.rect(640, py + 78, 90, 18, INK)
    c.text(40, py + 130, "BENGHAZI HARBOUR, LIBYA", 1, WHITE)

    # Row 2: two columns
    y = 486
    c.hline(40, y, 944, INK, 3)
    y += 16
    # Left: NATO AWACS
    c.text(40, y, "NATO SENDS AWACS", 2, RED)
    y2 = c.para(40, y + 26, "NATO SENDS AWACS TO POLAND", 3, INK, 452)
    y2 = c.para(40, y2 + 8, "Alliance moves early-warning jets after missiles land on NATO soil",
                2, GREY, 452)
    # radar graphic: concentric arcs + sweep
    rx, ry = 40, y2 + 14
    c.rect(rx, ry, 452, 92, NAVY)
    for r in (78, 56, 34):
        for a in range(0, 181, 4):
            dx = int(r * math.cos(math.radians(a)))
            dy = int(r * math.sin(math.radians(180 - a)))
            c.set(rx + 226 + dx, ry + 88 - dy, GOLD)
    c.circle(rx + 226, ry + 88, 4, RED)
    # Right: Riyadh tower
    c.text(532, y, "SAUDI ARABIA", 2, RED)
    y3 = c.para(532, y + 26, "HOUTHIS HIT RIYADH TOWER, 11 HURT", 3, INK, 452)
    y3 = c.para(532, y3 + 8, "Second strike on PIF Tower in under a week, civil defence says",
                2, GREY, 452)
    tx, ty = 532, y3 + 14
    c.rect(tx, ty, 452, 92, DUSK2)
    c.rect(tx, ty + 46, 452, 46, DUSK1)
    c.rect(tx + 200, ty + 8, 52, 84, TOWER)
    c.rect(tx + 212, ty, 28, 10, TOWER)
    c.rect(tx + 60, ty + 40, 90, 52, TOWER)
    c.rect(tx + 330, ty + 52, 70, 40, TOWER)
    c.circle(tx + 400, ty + 18, 12, GOLD)

    # Row 3: three briefs
    y = 800
    c.hline(40, y, 944, INK, 3)
    y += 14
    cols = [
        ("HUAWEI CONVICTED IN US TRIAL",
         "Guilty over Iran business in sprawling criminal case"),
        ("TRUMP GIVES GIULIANI MEDAL OF FREEDOM",
         "Ex-mayor honoured at the White House"),
        ("700,000 RUSSIAN TROOPS KILLED",
         "New analysis counts war dead near five-year mark"),
    ]
    for i, (hd, dk) in enumerate(cols):
        x = 40 + i * 320
        c.para(x, y, hd, 2, INK, 296)
        c.para(x, y + 52, dk, 2, GREY, 296)
        if i < 2:
            c.vline(x + 304, y, 86, GREY, 2)

    # Also-today strip
    y = 922
    c.rect(40, y, 944, 62, NAVY)
    c.text(56, y + 10, "ALSO TODAY:", 2, GOLD)
    c.para(56, y + 34, "GTA 6 OUT SINCE NOV 19 - ENGLAND LEVEL T20 SERIES - "
           "S KOREA MINISTER QUITS IN EXAM SCANDAL - UN COURT: MYANMAR "
           "GUILTY OVER ROHINGYA - WAYMO PULLS DRIVERLESS TAXIS OFF "
           "FREEWAYS - CIA, ODNI HIT BY BREACH", 1, WHITE, 912, lh=10)

    # Footer
    c.text(40, 996, "SUMMARY OF 25 NOVEMBER 2026 - SOURCES: REUTERS, RFE/RL",
           1, GREY)


def png_bytes(c):
    raw = bytearray()
    for yy in range(c.h):
        raw.append(0)
        raw += c.px[yy * c.w * 3:(yy + 1) * c.w * 3]

    def chunk(t, data):
        return (struct.pack(">I", len(data)) + t + data +
                struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    c = Canvas(W, H, PAPER)
    draw(c)
    data = png_bytes(c)
    path = os.path.join(out, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    # Read-back verify: magic, size, dims.
    back = open(path, "rb").read()
    assert back[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG magic"
    assert len(back) <= 1024 * 1024, "entry.png over 1 MiB: %d" % len(back)
    w, h = struct.unpack(">II", back[16:24])
    assert (w, h) == (W, H), "bad dims %dx%d" % (w, h)
    print("entry.png: %d bytes, %dx%d, sha256 %s" %
          (len(back), w, h, hashlib.sha256(back).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
