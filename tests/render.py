"""Rendu de texte et mesure d'encre (Pillow)."""
from PIL import Image, ImageDraw, ImageFont


def render(font_path: str, text: str, px: int) -> Image.Image:
    """Texte noir sur fond blanc, en niveaux de gris, une ligne par '\\n'."""
    font = ImageFont.truetype(font_path, px)
    lines = text.split("\n")
    width = max(int(font.getlength(line)) for line in lines) + 2 * px
    line_h = int(px * 1.4)
    img = Image.new("L", (max(width, 1), line_h * len(lines) + px), 255)
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((px, px // 2 + i * line_h + px), line, font=font, fill=0, anchor="ls")
    return img


def ink_runs(font_path: str, char: str, y_units: int) -> list[int]:
    """Longueurs (en unités de la police, rendue à 1000 px = 1000 unités/em)
    des segments d'encre sur la ligne y_units au-dessus de la ligne de base."""
    font = ImageFont.truetype(font_path, 1000)
    img = Image.new("L", (1600, 1400), 255)
    baseline = 1100
    ImageDraw.Draw(img).text((300, baseline), char, font=font, fill=0, anchor="ls")
    row = [img.getpixel((x, baseline - y_units)) < 128 for x in range(img.width)]
    runs, n = [], 0
    for dark in row + [False]:
        if dark:
            n += 1
        elif n:
            runs.append(n)
            n = 0
    return runs
