"""Étape 1 (FontForge) : contours et largeurs.

Lancer avec : fontforge -script build.py
"""
import os
import sys

import fontforge
import psMat

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import config  # noqa: E402
from lib.classify import classify  # noqa: E402


def ink_width(glyph):
    xmin, _, xmax, _ = glyph.boundingBox()
    return xmax - xmin


def fit_wide(glyph):
    """Réduit horizontalement un glyphe dont l'encre déborde de la cellule."""
    room = config.CELL - 2 * config.MARGIN
    w = ink_width(glyph)
    if w > room:
        glyph.transform(psMat.scale(room / w, 1.0))


def center(glyph):
    """Centre l'encre dans la cellule et fixe la largeur."""
    if glyph.foreground.isEmpty():
        glyph.width = config.CELL
        return
    xmin, _, xmax, _ = glyph.boundingBox()
    dx = round((config.CELL - (xmax - xmin)) / 2 - xmin)
    glyph.transform(psMat.translate(dx, 0))
    glyph.width = config.CELL


def main():
    font = fontforge.open(config.SOURCE)
    for glyph in font.glyphs():
        if glyph.glyphname in config.ZERO_WIDTH:
            glyph.width = 0
            continue
        kind = classify(glyph.width, config.CELL, config.NEAR_TOLERANCE)
        if kind == "wide" or ink_width(glyph) > config.CELL - 2 * config.MARGIN:
            fit_wide(glyph)
        center(glyph)
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    font.generate(os.path.join(HERE, config.STAGE1), flags=("opentype",))
    font.close()


main()
