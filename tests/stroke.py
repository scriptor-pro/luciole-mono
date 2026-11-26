"""Contreformes fermées d'un glyphe rendu (Pillow)."""
from PIL import Image, ImageDraw, ImageFont


PX = 200          # taille de rendu : 1 unité ≈ 0,2 px


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


PARTS_PX = 60     # 1 px ≈ 17 unités ≈ VISIBLE_GAP : deux morceaux plus proches se soudent


def ink_parts(font_path: str, char: str, px: int = PARTS_PX) -> int:
    """Nombre de morceaux d'encre séparés (connexité 4) du glyphe rendu."""
    font = ImageFont.truetype(font_path, px)
    img = Image.new("L", (px * 3, px * 3), 255)
    ImageDraw.Draw(img).text((px, px * 2), char, font=font, fill=0, anchor="ls")
    w, h = img.size
    data = img.tobytes()
    dark = {i for i, v in enumerate(data) if v < 128}
    count = 0
    while dark:
        count += 1
        stack = [dark.pop()]
        while stack:
            i = stack.pop()
            x = i % w
            for j in (i - w, i + w, i - 1 if x else -1, i + 1 if x < w - 1 else -1):
                if j in dark:
                    dark.remove(j)
                    stack.append(j)
    return count
