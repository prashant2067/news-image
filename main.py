"""Sum up 25 November's world news in one image.

Deterministic, offline PNG generator. Writes one image to /output/entry.png.
Uses only the Python standard library (zlib, struct, os) plus a built-in
bitmap font, so it runs without network and produces identical bytes on
every run — exactly as make.fun's news-image bounty requires.
"""

import os
import struct
import zlib


FONT_W = 5
FONT_H = 7
CHAR_SPACING = 1
LINE_SPACING = 4

FONT = {
    " ": [0, 0, 0, 0, 0],
    "!": [0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    '"': [0b01110, 0b00000, 0b00000, 0b00000, 0b00000],
    "#": [0b00100, 0b01110, 0b00100, 0b01110, 0b00100],
    "$": [0b00100, 0b10111, 0b01110, 0b11101, 0b00100],
    "%": [0b11001, 0b01010, 0b00100, 0b01010, 0b10011],
    "&": [0b01110, 0b10001, 0b01010, 0b00100, 0b11011],
    "'": [0b00100, 0b00000, 0b00000, 0b00000, 0b00000],
    "(": [0b00111, 0b01000, 0b10000, 0b01000, 0b00111],
    ")": [0b11100, 0b00010, 0b00001, 0b00010, 0b11100],
    "*": [0b00100, 0b01010, 0b11111, 0b01010, 0b00100],
    "+": [0b00100, 0b00100, 0b11111, 0b00100, 0b00100],
    ",": [0b00000, 0b00000, 0b00100, 0b01000, 0b10000],
    "-": [0b00000, 0b00000, 0b11111, 0b00000, 0b00000],
    ".": [0b00000, 0b00000, 0b00000, 0b00100, 0b00100],
    "/": [0b10000, 0b01000, 0b00100, 0b00010, 0b00001],
    "0": [0b01110, 0b10001, 0b10011, 0b10101, 0b01110],
    "1": [0b00100, 0b01100, 0b00100, 0b00100, 0b11111],
    "2": [0b01110, 0b10001, 0b00001, 0b01110, 0b10000],
    "3": [0b01110, 0b10001, 0b00110, 0b10001, 0b01110],
    "4": [0b00011, 0b00101, 0b01001, 0b11111, 0b00001],
    "5": [0b11111, 0b10000, 0b11110, 0b00001, 0b11110],
    "6": [0b01110, 0b10000, 0b11110, 0b10001, 0b01110],
    "7": [0b11111, 0b00001, 0b00010, 0b00100, 0b01000],
    "8": [0b01110, 0b10001, 0b01110, 0b10001, 0b01110],
    "9": [0b01110, 0b10001, 0b01111, 0b00001, 0b01110],
    ":": [0b00000, 0b00100, 0b00000, 0b00100, 0b00000],
    ";": [0b00000, 0b00100, 0b00000, 0b00100, 0b00100],
    "<": [0b00010, 0b00100, 0b01000, 0b00100, 0b00010],
    "=": [0b00000, 0b11111, 0b00000, 0b11111, 0b00000],
    ">": [0b01000, 0b00100, 0b00010, 0b00100, 0b01000],
    "?": [0b01110, 0b10001, 0b00001, 0b00010, 0b00000],
    "@": [0b01110, 0b10001, 0b01011, 0b01101, 0b00010],
    "A": [0b01110, 0b10001, 0b10001, 0b11111, 0b10001],
    "B": [0b11110, 0b10001, 0b01110, 0b10001, 0b11110],
    "C": [0b01110, 0b10000, 0b10000, 0b10000, 0b01110],
    "D": [0b11110, 0b10001, 0b10001, 0b10001, 0b11110],
    "E": [0b11111, 0b10000, 0b11110, 0b10000, 0b11111],
    "F": [0b11111, 0b10000, 0b11110, 0b10000, 0b10000],
    "G": [0b01110, 0b10000, 0b10111, 0b10001, 0b01111],
    "H": [0b10001, 0b10001, 0b11111, 0b10001, 0b10001],
    "I": [0b11111, 0b00100, 0b00100, 0b00100, 0b11111],
    "J": [0b11111, 0b00001, 0b00001, 0b10001, 0b01110],
    "K": [0b10001, 0b10010, 0b10100, 0b10010, 0b10001],
    "L": [0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    "M": [0b10001, 0b11011, 0b10101, 0b10001, 0b10001],
    "N": [0b10001, 0b11001, 0b10101, 0b10011, 0b10001],
    "O": [0b01110, 0b10001, 0b10001, 0b10001, 0b01110],
    "P": [0b11110, 0b10001, 0b11110, 0b10000, 0b10000],
    "Q": [0b01110, 0b10001, 0b10001, 0b10101, 0b00111],
    "R": [0b11110, 0b10001, 0b11110, 0b10100, 0b10001],
    "S": [0b01111, 0b10000, 0b01110, 0b00001, 0b11110],
    "T": [0b11111, 0b00100, 0b00100, 0b00100, 0b00100],
    "U": [0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "V": [0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    "W": [0b10001, 0b10001, 0b10101, 0b11011, 0b10001],
    "X": [0b10001, 0b01010, 0b00100, 0b01010, 0b10001],
    "Y": [0b10001, 0b01010, 0b00100, 0b00100, 0b00100],
    "Z": [0b11111, 0b00010, 0b00100, 0b01000, 0b11111],
    "[": [0b11111, 0b10000, 0b10000, 0b10000, 0b11111],
    "\\": [0b00001, 0b00010, 0b00100, 0b01000, 0b10000],
    "]": [0b11111, 0b00001, 0b00001, 0b00001, 0b11111],
    "^": [0b00100, 0b01010, 0b10001, 0b00000, 0b00000],
    "_": [0b00000, 0b00000, 0b00000, 0b00000, 0b11111],
    "`": [0b00100, 0b00000, 0b00000, 0b00000, 0b00000],
    "a": [0b00000, 0b01110, 0b00001, 0b01111, 0b10001],
    "b": [0b10000, 0b01110, 0b10001, 0b10001, 0b01110],
    "c": [0b00000, 0b01110, 0b10000, 0b10000, 0b01110],
    "d": [0b00001, 0b01111, 0b10001, 0b10001, 0b01111],
    "e": [0b00000, 0b01110, 0b11111, 0b10000, 0b01110],
    "f": [0b00110, 0b01001, 0b11110, 0b00001, 0b00011],
    "g": [0b00000, 0b01110, 0b10001, 0b01111, 0b00001],
    "h": [0b10000, 0b01110, 0b10001, 0b10001, 0b10001],
    "i": [0b00100, 0b00000, 0b01110, 0b00100, 0b00100],
    "j": [0b00001, 0b00000, 0b01111, 0b10001, 0b01110],
    "k": [0b10000, 0b10010, 0b10100, 0b11000, 0b10011],
    "l": [0b01110, 0b00100, 0b00100, 0b00100, 0b00100],
    "m": [0b00000, 0b01110, 0b10101, 0b10101, 0b10001],
    "n": [0b00000, 0b01110, 0b10001, 0b10001, 0b10001],
    "o": [0b00000, 0b01110, 0b10001, 0b10001, 0b01110],
    "p": [0b00000, 0b01110, 0b10001, 0b01110, 0b10000],
    "q": [0b00000, 0b01110, 0b10001, 0b01110, 0b00001],
    "r": [0b00000, 0b01110, 0b10000, 0b10000, 0b10000],
    "s": [0b00000, 0b01111, 0b10000, 0b01111, 0b00001],
    "t": [0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    "u": [0b00000, 0b10001, 0b10001, 0b10001, 0b01110],
    "v": [0b00000, 0b10001, 0b10001, 0b01010, 0b00100],
    "w": [0b00000, 0b10001, 0b10101, 0b11011, 0b10001],
    "x": [0b00000, 0b10001, 0b01010, 0b00100, 0b01010],
    "y": [0b00000, 0b10001, 0b01010, 0b00100, 0b00100],
    "z": [0b00000, 0b11111, 0b00100, 0b01000, 0b11111],
    "{": [0b00111, 0b01000, 0b10000, 0b01000, 0b00111],
    "|": [0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    "}": [0b11100, 0b00010, 0b00001, 0b00010, 0b11100],
    "~": [0b00000, 0b11011, 0b00000, 0b00000, 0b00000],
}

# Lowercase letters missing from FONT fall back to their uppercase shape.
for _uc in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    _lc = _uc.lower()
    if _lc not in FONT:
        FONT[_lc] = FONT[_uc]


def _chunk(kind, data):
    crc = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def encode_png(width, height, pixels):
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for r, g, b in row:
            raw.append(r)
            raw.append(g)
            raw.append(b)
    compressed = zlib.compress(bytes(raw), 6)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = _chunk(b"IDAT", compressed)
    iend = _chunk(b"IEND", b"")
    return sig + _chunk(b"IHDR", ihdr) + idat + iend


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVY = (18, 32, 64)
STEEL = (70, 110, 160)
AMBER = (220, 140, 30)
GRAY = (120, 120, 120)
LIGHT = (240, 244, 250)


def draw_text(canvas, width, x, y, text, color, scale=1, font=FONT):
    cx = x
    for ch in text:
        glyph = font.get(ch, font[" "])
        for col in range(FONT_W):
            bits = glyph[col]
            for row in range(FONT_H):
                if bits >> row & 1:
                    px = cx + col * scale
                    py = y + row * scale
                    if 0 <= px < width and py < len(canvas):
                        for sx in range(scale):
                            for sy in range(scale):
                                nx, ny = px + sx, py + sy
                                if 0 <= nx < width and ny < len(canvas):
                                    canvas[ny][nx] = color
        cx += (FONT_W + CHAR_SPACING) * scale
    return cx


def text_width(text, scale=1):
    return (len(text) * (FONT_W + CHAR_SPACING) - CHAR_SPACING) * scale


def wrap_text(text, max_width, scale=1):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


TITLE = "WORLD NEWS — 25 NOVEMBER 2026"
TITLE_SUB = "One image, one day — summarized for make.fun"

NEWS = [
    ("MIDDLE EAST",
     "Saudi-led coalition intercepted four drones over the Eastern Province "
     "(Ras Tanura); a Houthi drone strike on Riyadh's King Abdullah Financial "
     "District injured 11 people."),
    ("STRAIT OF HORMUZ",
     "Iran's IRGC Navy reported two 'rogue' oil tankers struck naval mines "
     "and caught fire while crossing the strait by an unauthorized route."),
    ("RUSSIA - UKRAINE",
     "President Putin said Moscow's response to Ukrainian attacks on Russian "
     "oil refineries is inevitable, despite a US request to halt them."),
    ("SPACE",
     "China launched Shenzhou-24, carrying Pakistan's first astronaut "
     "(Muhammad Zeeshan Ali) to the Tiangong space station for ~90 experiments."),
    ("ARTIFICIAL INTELLIGENCE",
     "UN Secretary-General Guterres called for global cooperation to set "
     "guardrails on AI development at a Security Council debate."),
    ("UNITED STATES",
     "President Trump said a pardon for Nvidia CEO Jensen Huang is "
     "'always an option,' though he did not think it would be necessary."),
    ("GAZA",
     "Rapper Macklemore released 'Where's Our Love,' pledging proceeds to a "
     "fund for Palestinian mothers and children in Gaza."),
]


WIDTH = 860
HEIGHT = 900
PAD = 40


def build():
    canvas = [[WHITE for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for y in range(HEIGHT):
        canvas[y][0] = NAVY
        canvas[y][WIDTH - 1] = NAVY
    for x in range(WIDTH):
        canvas[0][x] = NAVY
        canvas[HEIGHT - 1][x] = NAVY

    ty = PAD
    draw_text(canvas, WIDTH, PAD, ty, TITLE, NAVY, scale=2)
    ty += FONT_H * 2 + LINE_SPACING
    draw_text(canvas, WIDTH, PAD, ty, TITLE_SUB, GRAY, scale=1)
    ty += FONT_H + LINE_SPACING * 3

    for x in range(PAD, WIDTH - PAD):
        canvas[ty][x] = STEEL
    ty += LINE_SPACING * 2

    for idx, (category, body) in enumerate(NEWS, start=1):
        chip_x = PAD
        chip_y = ty
        chip_h = FONT_H + 6
        chip_w = text_width(category, scale=1) + 14
        for yy in range(chip_y, chip_y + chip_h):
            for xx in range(chip_x, min(chip_x + chip_w, WIDTH)):
                if 0 <= yy < HEIGHT and 0 <= xx < WIDTH:
                    canvas[yy][xx] = LIGHT
        draw_text(canvas, WIDTH, PAD + 7, chip_y + 3, category, NAVY, scale=1)
        bx = chip_x + chip_w + 6
        by = chip_y + chip_h // 2 - 2
        for yy in range(by, by + 5):
            for xx in range(bx, bx + 5):
                if 0 <= yy < HEIGHT and 0 <= xx < WIDTH:
                    canvas[yy][xx] = AMBER

        body_x = PAD
        body_y = chip_y + chip_h + 4
        max_w = WIDTH - PAD * 2
        for line in wrap_text(body, max_w, scale=1):
            draw_text(canvas, WIDTH, body_x, body_y, line, BLACK, scale=1)
            body_y += FONT_H + 2
        ty = body_y + LINE_SPACING * 2

    footer_y = HEIGHT - PAD - 10
    draw_text(canvas, WIDTH, PAD, footer_y, "Generated offline, deterministically — no network used.", GRAY, scale=1)
    footer_right = "make.fun news-image bounty"
    draw_text(canvas, WIDTH, WIDTH - PAD - text_width(footer_right, scale=1), footer_y,
              footer_right, GRAY, scale=1)

    return canvas


def main():
    out_dir = "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(out_dir, exist_ok=True)

    canvas = build()
    png_bytes = encode_png(WIDTH, HEIGHT, canvas)

    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as f:
        f.write(png_bytes)

    size = len(png_bytes)
    print(f"Wrote {out_path} ({WIDTH}x{HEIGHT}, {size} bytes)")


if __name__ == "__main__":
    main()
