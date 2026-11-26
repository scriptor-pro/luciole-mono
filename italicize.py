"""Étape 3 (fontTools) : les italiques sont les fontes droites finies,
penchées comme Luciole Italic (une oblique du droit, mêmes chasses)."""
import math
import os
import sys

from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import config  # noqa: E402

ITALIC, BOLD, REGULAR = 1, 32, 64          # bits de OS/2.fsSelection


def slant_glyphs(font, angle, y0):
    t = math.tan(math.radians(angle))
    glyf, hmtx = font["glyf"], font["hmtx"]
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.isComposite():
            raise ValueError(f"glyphe composé inattendu : {name}")
        if not g.numberOfContours:
            continue
        for i, (x, y) in enumerate(g.coordinates):
            g.coordinates[i] = (round(x + (y - y0) * t), y)
        g.recalcBounds(glyf)
        hmtx[name] = (hmtx[name][0], g.xMin)


def set_italic_metadata(font, angle):
    font["post"].italicAngle = -angle
    hhea = font["hhea"]
    hhea.caretSlopeRise = 1000
    hhea.caretSlopeRun = round(1000 * math.tan(math.radians(angle)))
    # l'inclinaison pivote autour de SLANT_Y0 : décalage à la ligne de base
    hhea.caretOffset = round(-config.SLANT_Y0 * math.tan(math.radians(angle)))
    os2 = font["OS/2"]
    os2.fsSelection = (os2.fsSelection | ITALIC) & ~REGULAR
    font["head"].macStyle |= 2


def set_italic_names(font, ps_name, style):
    name = font["name"]
    full = f"{config.FAMILY} {style}"
    values = {2: style, 3: f"{full};{ps_name}", 4: full, 6: ps_name, 17: style}
    name.names = [r for r in name.names if r.nameID not in values]
    for name_id, value in values.items():
        name.setName(value, name_id, 3, 1, 0x409)
        name.setName(value, name_id, 1, 0, 0)


def main(uprights):
    """Penche les droits demandés (Regular → Italic, Bold → BoldItalic)."""
    for ps_style, (upright, style) in config.ITALICS.items():
        if upright not in uprights:
            continue
        font = TTFont(os.path.join(HERE, "dist", f"LucioleMono-{upright}.ttf"))
        slant_glyphs(font, config.SLANT, config.SLANT_Y0)
        set_italic_metadata(font, config.SLANT)
        set_italic_names(font, f"LucioleMono-{ps_style}", style)
        font.save(os.path.join(HERE, "dist", f"LucioleMono-{ps_style}.ttf"))


if __name__ == "__main__":
    main(sys.argv[1:] or [u for u, _ in config.ITALICS.values()])
