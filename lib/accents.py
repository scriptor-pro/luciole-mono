"""Séparer un accent de sa lettre de base (Luciole n'a pas de composites).

Contour = liste de points (x, y), dans l'ordre du tracé."""
import unicodedata

# lettre de base Unicode → glyphe de base cherché dans le glyphe accentué
# (l'accent remplace le point de i et j)
BASE_OF = {"i": "dotlessi", "j": "dotlessj", "l": "l", "r": "r"}


def glyph_contours(ttfont, name):
    """Contours d'un glyphe TrueType (fontTools), points arrondis."""
    glyf = ttfont["glyf"]
    g = glyf[name]
    if g.numberOfContours <= 0:
        return []
    coords = g.getCoordinates(glyf)[0]
    contours, start = [], 0
    for end in g.endPtsOfContours:
        contours.append([(round(x), round(y)) for x, y in coords[start:end + 1]])
        start = end + 1
    return contours


def _shift(contour, dx):
    return [(x + dx, y) for x, y in contour]


def split_accent(accented, base):
    """Renvoie (contours de l'accent, dx) où dx est le décalage horizontal de
    la base dans le glyphe accentué ; (accented, None) si la base n'y est pas.

    Les dx candidats viennent des premiers points de chaque paire de contours
    de même longueur ; un dx convient si tous les contours de la base, décalés,
    se retrouvent dans le glyphe accentué."""
    if not base:
        return accented, None
    candidates = {c[0][0] - base[0][0][0] for c in accented
                  if len(c) == len(base[0]) and c[0][1] == base[0][0][1]}
    for dx in sorted(candidates, key=abs):
        remaining = list(accented)
        for contour in base:
            shifted = _shift(contour, dx)
            if shifted not in remaining:
                break
            remaining.remove(shifted)
        else:
            return remaining, dx
    return accented, None


def derived_glyphs(cmap, bases):
    """{glyphe accentué: glyphe de base} pour les bases redessinées."""
    out = {}
    for code, name in cmap.items():
        decomposition = unicodedata.decomposition(chr(code)).split()
        codes = [c for c in decomposition if not c.startswith("<")]
        if not codes:
            continue
        if any(unicodedata.category(chr(int(c, 16))).startswith("L")
               for c in codes[1:]):
            continue                      # ligature (ĳ) : pas un accent
        base = BASE_OF.get(chr(int(codes[0], 16)))
        if base in bases and name != base:
            out[name] = base
    return out
