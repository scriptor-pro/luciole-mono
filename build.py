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
from lib.scanline import gap_rows, ink_groups, median_gap, median_stem, min_distance  # noqa: E402
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
    leurs fûts tiennent dans la place. Sinon, les accents sont mis de côté
    avant toute mesure (_split_parts) :
    - au-dessus ou au-dessous de la lettre (Ã, Ö) : réduits comme elle, pas
      épaissis ;
    - à côté (caron de ď, apostrophe de ŉ) : réduits d'un facteur uniforme,
      leur place est réservée, puis ils sont reposés à au moins SEPARATION
      de la lettre.
    La lettre seule passe par _fit_body."""
    room = room or config.CELL - 2 * config.MARGIN
    width = ink_width(glyph)
    if width <= room:
        return
    if glyph.glyphname in config.CONDENSE_EXTEND and _condense_counters(glyph, room, width):
        pass
    else:
        marks, sides = _split_parts(glyph)
        ks = max(config.SIDE_MIN_SCALE, min(1.0, room / width))
        body_room = room
        for contours, box, right, gap in sides:
            pivot = box[0] if right else box[2]
            for c in contours:
                c.transform(psMat.compose(psMat.translate(-pivot, -box[3]), psMat.compose(
                    psMat.scale(ks), psMat.translate(pivot, box[3]))))
            body_room -= ks * (box[2] - box[0]) + max(config.SEPARATION, ks * gap)
        k = _fit_body(glyph, body_room)
        layer = glyph.foreground
        for contour in marks:
            contour.transform(psMat.scale(k, 1.0))
            layer += contour
        x0, _, x1, _ = layer.boundingBox()
        for contours, box, right, gap in sides:
            sx0 = min(c.boundingBox()[0] for c in contours)
            sx1 = max(c.boundingBox()[2] for c in contours)
            sep = max(config.SEPARATION, ks * gap)
            dx = (x1 + sep - sx0) if right else (x0 - sep - sx1)
            for c in contours:
                c.transform(psMat.translate(dx, 0))
                layer += c
        glyph.foreground = layer
        rest = ink_width(glyph)
        if rest > room:              # marques plus larges que la lettre (⁂)
            glyph.transform(psMat.scale(room / rest, 1.0))
    glyph.removeOverlap()
    glyph.correctDirection()
    glyph.round()


def _fit_body(glyph, room):
    """Met la lettre (sans accents) dans room : échelle horizontale k puis
    épaississement de EMBOLDEN·trait·(1 − k), où trait est l'épaisseur propre
    au glyphe (mesurée), sans réduire l'espace intérieur médian sous MIN_GAP
    (sinon tache) : si cette limite joue, k est recalculé pour que
    k·W + k·gap − MIN_GAP = place. Renvoie le facteur horizontal total
    (appliqué autour de x = 0), pour les accents."""
    width = ink_width(glyph)
    if width <= room:
        return 1.0
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
        k *= room / rest
    return k


def _contour_count(glyph):
    probe = glyph.foreground.dup()
    probe.removeOverlap()
    return len(probe)


def _split_parts(glyph):
    """Retire du glyphe ses accents et les renvoie : (marques, latéraux).

    - marques : morceaux entièrement au-dessus ou au-dessous du plus grand
      (trémas de Ä Ö, tilde de Ã, anneau de Å). Épaissis avec la lettre, les
      points d'un tréma se soudaient ; mesurés avec elle, ils faisaient
      croire à des traits plus fins.
    - latéraux : petits morceaux (moins de SIDE_ACCENT_AREA de la lettre)
      entièrement à droite ou à gauche (caron de ď, apostrophe de ŉ), en
      (contours, boîte, à_droite, écart à la lettre).
    Les morceaux de même taille (points de …, chevrons de «) restent."""
    contours = list(glyph.foreground)
    flagged = _flagged(glyph)
    groups = ink_groups(flagged)
    if len(groups) < 2:
        return [], []

    def box(group):
        pts = [p for i in group for p in flagged[i]]
        return (min(p[0] for p in pts), min(p[1] for p in pts),
                max(p[0] for p in pts), max(p[1] for p in pts))

    def area(b):
        return (b[2] - b[0]) * (b[3] - b[1])
    main = max(groups, key=lambda g: area(box(g)))
    body = box(main)
    marks, sides, taken = [], [], set()
    for g in groups:
        if g is main:
            continue
        b = box(g)
        if b[1] >= body[3] or b[3] <= body[1]:
            marks += [contours[i].dup() for i in g]
        elif area(b) < config.SIDE_ACCENT_AREA * area(body) and (b[0] >= body[2] or b[2] <= body[0]):
            right = b[0] >= body[2]
            sides.append(([contours[i].dup() for i in g], b, right,
                          b[0] - body[2] if right else body[0] - b[2]))
        else:
            continue
        taken.update(g)
    # les morceaux d'un même côté (º et son trait dans №) forment un bloc :
    # une seule place réservée, un seul déplacement
    merged = {}
    for contours_, b, right, gap in sides:
        if right in merged:
            c0, b0, _, g0 = merged[right]
            merged[right] = (c0 + contours_, (min(b0[0], b[0]), min(b0[1], b[1]),
                                              max(b0[2], b[2]), max(b0[3], b[3])),
                             right, min(g0, gap))
        else:
            merged[right] = (contours_, b, right, gap)
    sides = list(merged.values())
    if taken:
        keep = fontforge.layer()
        keep.is_quadratic = glyph.foreground.is_quadratic
        for i, c in enumerate(contours):
            if i not in taken:
                keep += c
        glyph.foreground = keep
    return marks, sides


def _separation(glyph):
    """Plus petit blanc entre deux morceaux d'encre (None s'il n'y en a qu'un) :
    points de …, chevrons de «, apostrophe de ŉ, caron de ď."""
    flagged = _flagged(glyph)
    groups = ink_groups(flagged)
    if len(groups) < 2:
        return None, 1
    parts = [[flagged[i] for i in g] for g in groups]
    return min(min_distance(a, b) for n, a in enumerate(parts)
               for b in parts[n + 1:]), len(groups)


def _visible_gaps(glyph):
    return gap_rows(_flagged(glyph), config.VISIBLE_GAP)


def _embolden_keeping_counters(glyph, delta):
    """Épaissit de delta ; réessaie avec 75 % de l'épaisseur, jusqu'à
    renoncer, si :
    - une contreforme se bouche (moins de contours) ;
    - des encoches ouvertes disparaissent (moins de KEEP_GAPS des espaces
      visibles, comme le bas du M) ;
    - deux morceaux d'encre séparés se rapprochent à moins de SEPARATION
      (points de …, chevrons de «)."""
    target = _contour_count(glyph)
    gaps = _visible_gaps(glyph)
    sep, parts = _separation(glyph)
    saved = glyph.foreground.dup()
    while delta >= 4:
        embolden(glyph, delta, horizontal=True)
        new_sep, new_parts = _separation(glyph)
        if (_contour_count(glyph) >= target
                and _visible_gaps(glyph) >= config.KEEP_GAPS * gaps
                and (sep is None or (new_parts >= parts
                                     and new_sep >= min(config.SEPARATION, sep)))):
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


ACCENT_MIN_SCALE = 0.6      # réduction maximale d'un accent latéral (ľ, ŀ)


def _fit_side_accent(base, accent):
    """Accent qui dépasse à droite de la cellule. Au-dessus de la lettre
    (ĵ), on le pousse simplement vers la gauche. À côté (caron de ľ, point de
    ŀ en gras) : on glisse tout le glyphe vers la gauche (jusqu'à MARGIN/2), ce qui
    garde l'écart entre fût et accent ; s'il dépasse encore, on réduit
    l'accent autour de son bord gauche. Pousser l'accent seul le soudait au
    fût."""
    limit = config.CELL - config.MARGIN
    a0 = min(c.boundingBox()[0] for c in accent)
    a1 = max(c.boundingBox()[2] for c in accent)
    if a1 <= limit:
        return
    if min(c.boundingBox()[1] for c in accent) >= base.boundingBox()[3]:
        shift = psMat.translate(limit - a1, 0)     # accent au-dessus (ĵ) : sans risque
        for c in accent:
            c.transform(shift)
        return
    slide = min(a1 - limit, max(0, base.boundingBox()[0] - config.MARGIN / 2))
    move = psMat.translate(-slide, 0)
    base.transform(move)
    for c in accent:
        c.transform(move)
    a0, a1 = a0 - slide, a1 - slide
    if a1 > limit:
        f = max(ACCENT_MIN_SCALE, (limit - a0) / (a1 - a0))
        ys = [c.boundingBox()[1] for c in accent] + [c.boundingBox()[3] for c in accent]
        cy = (min(ys) + max(ys)) / 2
        m = psMat.compose(psMat.translate(-a0, -cy),
                          psMat.compose(psMat.scale(f), psMat.translate(a0, cy)))
        for c in accent:
            c.transform(m)


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
        for contour in moved:
            contour.transform(psMat.translate(shift, 0))
        layer = font[base].foreground.dup()
        _fit_side_accent(layer, moved)
        for contour in moved:
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
