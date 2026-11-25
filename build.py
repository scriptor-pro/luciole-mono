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
from lib import narrow  # noqa: E402
from lib.accents import derived_glyphs, split_accent  # noqa: E402


def ink_width(glyph):
    xmin, _, xmax, _ = glyph.boundingBox()
    return xmax - xmin


STEM = 112   # épaisseur du fût de n dans Luciole Regular (mesurée)


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


def _embolden(glyph, delta):
    """Épaissit chaque trait de delta (delta/2 de chaque côté) avec une plume
    ronde à jointures en onglet (angles vifs conservés), puis ramène le glyphe
    à sa hauteur d'origine pour garder ligne de base et hauteur d'x."""
    _, ymin, _, ymax = glyph.boundingBox()
    outline = glyph.foreground.dup()
    glyph.stroke("circular", delta, "butt", "miter")
    for contour in outline:
        glyph.foreground += contour
    glyph.removeOverlap()
    _, ymin2, _, ymax2 = glyph.boundingBox()
    sy = (ymax - ymin) / (ymax2 - ymin2)
    glyph.transform(psMat.compose(psMat.translate(0, -ymin2),
                                  psMat.compose(psMat.scale(1, sy), psMat.translate(0, ymin))))


def _embolden_keeping_counters(glyph, delta):
    """Épaissit de delta ; si une contreforme se bouche (moins de contours),
    réessaie avec 75 % de l'épaisseur, jusqu'à renoncer."""
    target = _contour_count(glyph)
    saved = glyph.foreground.dup()
    while delta >= 4:
        _embolden(glyph, delta)
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


def rebuild_accented(font, originals):
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
        shift = narrow.STEM_CENTER[base] - (narrow.OLD_STEM_CENTER + dx)
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
    originals = {b: [c.dup() for c in font[b].foreground] for b in narrow.STEM_CENTER}
    for redesign in (narrow.redesign_i, narrow.redesign_j,
                     narrow.redesign_l, narrow.redesign_r):
        redesign(font, STEM, config.CELL)
    # locl tr/az/crh : i → idotaccent, qui doit suivre le nouveau i
    font["idotaccent"].foreground = font["i"].foreground.dup()
    font["idotaccent"].width = config.CELL
    rebuilt, unmatched = rebuild_accented(font, originals)
    rebuilt.append("idotaccent")
    print(f"accents reconstruits : {len(rebuilt)} ; non appariés (centrés) : "
          f"{', '.join(unmatched) or 'aucun'}")
    skip = set(config.NARROW_REDESIGN) | set(rebuilt)
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
