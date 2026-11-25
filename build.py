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
from lib.scanline import gap_rows, median_gap, median_stem  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from lib.accents import derived_glyphs, split_accent  # noqa: E402


def ink_width(glyph):
    xmin, _, xmax, _ = glyph.boundingBox()
    return xmax - xmin


GEOMETRY = measure(TTFont(config.SOURCE))
STEM = GEOMETRY["stem"]   # épaisseur du fût, mesurée sur la source


def _flagged(glyph):
    return [[(p.x, p.y, p.on_curve) for p in c] for c in glyph.foreground]


def fit_wide(glyph, room=None):
    """Ramène l'encre d'un glyphe large dans la cellule sans l'amincir.

    Les glyphes de config.CONDENSE_EXTEND (fûts verticaux purs, comme m)
    sont condensés par condenseExtend, qui rétrécit les contreformes, si
    leurs fûts tiennent dans la place. Sinon on met à l'échelle d'un facteur k
    puis on épaissit horizontalement de EMBOLDEN·trait·(1 − k), où trait est
    l'épaisseur propre au glyphe (mesurée), sans jamais réduire l'espace
    intérieur médian sous MIN_GAP (sinon le glyphe fait une tache) : si cette
    limite joue, k est recalculé pour que k·W + k·gap − MIN_GAP = place."""
    room = room or config.CELL - 2 * config.MARGIN
    width = ink_width(glyph)
    if width <= room:
        return
    if glyph.glyphname in config.CONDENSE_EXTEND and _condense_counters(glyph, room, width):
        pass
    else:
        min_gap = config.MIN_GAP * STEM
        gap = median_gap(_flagged(glyph), q=config.GAP_PERCENTILE)
        own = config.EMBOLDEN * (median_stem(_flagged(glyph)) or STEM)
        if own >= width / 2:                 # forme pleine (tiret, pavé)
            k, delta = room / width, 0
        else:
            k = max((room - own) / (width - own), 0.2)
            delta = own * (1 - k)
        if gap is not None and delta > k * gap - min_gap:
            k = min((room + min_gap) / (width + gap), room / width) \
                if k * gap > min_gap else room / width
            delta = max(k * gap - min_gap, 0)
        glyph.transform(psMat.scale(k, 1.0))
        if delta >= 4:
            _embolden_keeping_counters(glyph, delta)
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


def _visible_gaps(glyph):
    return gap_rows(_flagged(glyph), config.VISIBLE_GAP)


def _embolden_keeping_counters(glyph, delta):
    """Épaissit de delta ; si une contreforme se bouche (moins de contours)
    ou si des encoches ouvertes disparaissent (moins de KEEP_GAPS des espaces
    visibles, comme le bas du M), réessaie avec 75 % de l'épaisseur, jusqu'à
    renoncer."""
    target = _contour_count(glyph)
    gaps = _visible_gaps(glyph)
    saved = glyph.foreground.dup()
    while delta >= 4:
        embolden(glyph, delta, horizontal=True)
        if (_contour_count(glyph) >= target
                and _visible_gaps(glyph) >= config.KEEP_GAPS * gaps):
            return
        glyph.foreground = saved.dup()
        delta *= 0.75


def _condense_counters(glyph, room, width):
    """ink ≈ S + f·(W − S), S = somme des fûts : un essai donne S, le second
    vise la largeur exacte. Renvoie False (glyphe intact) si les fûts seuls
    ne laissent pas assez de place aux contreformes."""
    saved = glyph.foreground.dup()
    f0 = room / width
    glyph.condenseExtend(f0, 0)
    stems = (ink_width(glyph) - f0 * width) / (1 - f0)
    glyph.foreground = saved.dup()
    factor = (room - stems) / (width - stems)
    if factor < config.MIN_CONDENSE:
        return False
    glyph.condenseExtend(factor, 0)
    return True


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
        moved = [c.dup() for pts, c in zip(points, contours) if any(pts is a for a in accent)]
        right = max(c.boundingBox()[2] for c in moved) + shift
        shift -= max(0, right - (config.CELL - config.MARGIN))   # ex. caron de ľ
        layer = font[base].foreground.dup()
        for contour in moved:
            contour.transform(psMat.translate(shift, 0))
            layer += contour
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
        if glyph.glyphname == "zero" or glyph.glyphname.startswith("zero."):
            fit_wide(glyph, room=round(config.ZERO_INK * (config.CELL - 2 * config.MARGIN)))
            center(glyph)
            continue
        if glyph.glyphname == "I" and config.I_INK < 1:
            room = round(config.I_INK * (config.CELL - 2 * config.MARGIN))
            if not _condense_counters(glyph, room, ink_width(glyph)):
                fit_wide(glyph, room=room)
            center(glyph)
            continue
        kind = classify(glyph.width, config.CELL, config.NEAR_TOLERANCE)
        if kind == "wide" or ink_width(glyph) > config.CELL - 2 * config.MARGIN:
            fit_wide(glyph)
        center(glyph)
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    font.generate(os.path.join(HERE, config.STAGE1), flags=("opentype",))
    font.close()


main()
