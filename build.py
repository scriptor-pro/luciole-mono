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
from lib import narrow, symbols  # noqa: E402
from lib.outline import embolden  # noqa: E402
from lib.geometry import measure  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from lib.accents import derived_glyphs, split_accent  # noqa: E402


def ink_width(glyph):
    xmin, _, xmax, _ = glyph.boundingBox()
    return xmax - xmin


GEOMETRY = measure(TTFont(config.SOURCE))
STEM = GEOMETRY["stem"]   # épaisseur du fût, mesurée sur la source


def fit_wide(glyph):
    """Ramène l'encre d'un glyphe large dans la cellule sans l'amincir.

    Les glyphes de config.CONDENSE_EXTEND (fûts verticaux purs, comme m)
    sont condensés par condenseExtend, qui rétrécit les contreformes.
    Les autres (diagonales, ronds) sont mis à l'échelle d'un facteur k puis
    épaissis de STEM·(1 − k) pour retrouver leur graisse :
    k·W + STEM·(1 − k) = place disponible."""
    room = config.CELL - 2 * config.MARGIN
    width = ink_width(glyph)
    if width <= room:
        return
    if glyph.glyphname in config.CONDENSE_EXTEND:
        _condense_counters(glyph, room, width)
    else:
        k = max((room - STEM) / (width - STEM), 0.2)
        glyph.transform(psMat.scale(k, 1.0))
        _embolden_keeping_counters(glyph, config.EMBOLDEN * STEM * (1 - k))
        rest = ink_width(glyph)
        if rest > room:
            glyph.transform(psMat.scale(room / rest, 1.0))
    glyph.removeOverlap()
    glyph.correctDirection()
    glyph.round()


def _contour_count(glyph):
    probe = glyph.foreground.dup()
    probe.removeOverlap()
    return len(probe)


def _embolden_keeping_counters(glyph, delta):
    """Épaissit de delta ; si une contreforme se bouche (moins de contours),
    réessaie avec 75 % de l'épaisseur, jusqu'à renoncer."""
    target = _contour_count(glyph)
    saved = glyph.foreground.dup()
    while delta >= 4:
        embolden(glyph, delta)
        if _contour_count(glyph) >= target:
            return
        glyph.foreground = saved.dup()
        delta *= 0.75


def _condense_counters(glyph, room, width):
    """ink ≈ S + f·(W − S), S = somme des fûts : un essai donne S, le second
    vise la largeur exacte."""
    saved = glyph.foreground.dup()
    f0 = room / width
    glyph.condenseExtend(f0, 0)
    stems = (ink_width(glyph) - f0 * width) / (1 - f0)
    glyph.foreground = saved
    glyph.condenseExtend((room - stems) / (width - stems), 0)


def center(glyph):
    """Centre l'encre dans la cellule et fixe la largeur."""
    if glyph.foreground.isEmpty():
        glyph.width = config.CELL
        return
    xmin, _, xmax, _ = glyph.boundingBox()
    dx = round((config.CELL - (xmax - xmin)) / 2 - xmin)
    glyph.transform(psMat.translate(dx, 0))
    glyph.width = config.CELL


def _points(contours):
    return [[(round(p.x), round(p.y)) for p in c] for c in contours]


def rebuild_accented(font, originals, centers):
    """Reconstruit chaque lettre accentuée sur sa base redessinée : contours de
    l'accent d'origine, décalés comme le fût de la base. Renvoie (reconstruits,
    non appariés)."""
    cmap = {g.unicode: g.glyphname for g in font.glyphs() if g.unicode > 0}
    rebuilt, unmatched = [], []
    for name, base in sorted(derived_glyphs(cmap, set(originals)).items()):
        glyph = font[name]
        contours = list(glyph.foreground)
        points = _points(contours)
        accent, dx = split_accent(points, _points(originals[base]))
        if dx is None:
            unmatched.append(name)
            continue
        shift = centers[base] - (narrow.old_stem_center(GEOMETRY) + dx)
        layer = font[base].foreground.dup()
        for pts, contour in zip(points, contours):
            if any(pts is a for a in accent):
                moved = contour.dup()
                moved.transform(psMat.translate(shift, 0))
                layer += moved
        glyph.foreground = layer
        glyph.correctDirection()
        glyph.round()
        glyph.width = config.CELL
        rebuilt.append(name)
    return rebuilt, unmatched


def main():
    font = fontforge.open(config.SOURCE)
    narrow.slashed_zero(font)
    symbols.redesign_percents(font, STEM, config.CELL)
    redesigns = {"dotlessi": narrow.redesign_i, "dotlessj": narrow.redesign_j,
                 "l": narrow.redesign_l, "r": narrow.redesign_r}
    originals = {b: [c.dup() for c in font[b].foreground] for b in redesigns}
    centers = {b: f(font, GEOMETRY, config.CELL) for b, f in redesigns.items()}
    # locl tr/az/crh : i → idotaccent, qui doit suivre le nouveau i
    font["idotaccent"].foreground = font["i"].foreground.dup()
    font["idotaccent"].width = config.CELL
    rebuilt, unmatched = rebuild_accented(font, originals, centers)
    rebuilt.append("idotaccent")
    print(f"accents reconstruits : {len(rebuilt)} ; non appariés (centrés) : "
          f"{', '.join(unmatched) or 'aucun'}")
    skip = set(config.NARROW_REDESIGN) | set(rebuilt) | set(symbols.REDESIGNED)
    for glyph in font.glyphs():
        if glyph.glyphname in skip:
            continue
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
