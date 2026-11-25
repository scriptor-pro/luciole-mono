"""Épaisseur réelle des traits, quel que soit leur angle (érosion)."""
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import config
from lib.geometry import measure

PX = 200          # taille de rendu : 1 unité ≈ 0,2 px
STEM = measure(TTFont(config.SOURCE))["stem"]   # fût de la graisse testée


def stroke_survival(font_path: str, char: str, ratio: float = 0.75) -> float:
    """Part de l'encre qui survit à une érosion de largeur ratio × STEM.
    Un trait plus fin que cette largeur disparaît entièrement."""
    font = ImageFont.truetype(font_path, PX)
    img = Image.new("L", (PX * 2, PX * 2), 255)
    ImageDraw.Draw(img).text((PX // 2, PX * 3 // 2), char, font=font, fill=0, anchor="ls")
    size = int(ratio * STEM * PX / 1000) | 1          # taille impaire
    eroded = img.filter(ImageFilter.MaxFilter(size))
    ink = sum(p < 128 for p in img.tobytes())
    return sum(p < 128 for p in eroded.tobytes()) / ink


def holes(font_path: str, char: str) -> int:
    """Nombre de contreformes fermées (zones blanches isolées du fond)."""
    font = ImageFont.truetype(font_path, PX)
    img = Image.new("L", (PX * 2, PX * 2), 255)
    ImageDraw.Draw(img).text((PX // 2, PX * 3 // 2), char, font=font, fill=0, anchor="ls")
    w, h = img.size
    white = [[img.getpixel((x, y)) >= 128 for x in range(w)] for y in range(h)]
    seen = [[False] * w for _ in range(h)]
    count = 0
    for y0 in range(h):
        for x0 in range(w):
            if not white[y0][x0] or seen[y0][x0]:
                continue
            stack, border, size = [(x0, y0)], False, 0
            seen[y0][x0] = True
            while stack:
                x, y = stack.pop()
                size += 1
                if x in (0, w - 1) or y in (0, h - 1):
                    border = True
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and white[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            if not border and size > 4:
                count += 1
    return count
