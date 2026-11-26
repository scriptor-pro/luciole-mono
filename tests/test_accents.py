import pytest

import config

from lib.accents import derived_glyphs, glyph_contours, split_accent


def test_split_accent_finds_shifted_base():
    base = [[(0, 0), (10, 0), (10, 100), (0, 100)]]
    acc = [[(5, 0), (15, 0), (15, 100), (5, 100)], [(0, 120), (20, 120), (10, 140)]]
    accent, dx = split_accent(acc, base)
    assert dx == 5 and accent == [acc[1]]


def test_split_accent_without_base():
    accent, dx = split_accent([[(0, 0), (1, 1), (2, 0)]], [[(0, 0), (9, 9), (9, 0)]])
    assert dx is None


def test_derived_glyphs_maps_to_dotless_bases():
    cmap = {ord("í"): "iacute", ord("ĵ"): "jcircumflex", ord("ľ"): "lcaron",
            ord("ŕ"): "racute", ord("ł"): "lslash", ord("é"): "eacute",
            ord("ĳ"): "ij"}
    assert derived_glyphs(cmap, {"dotlessi", "dotlessj", "l", "r"}) == {
        "iacute": "dotlessi", "jcircumflex": "dotlessj",
        "lcaron": "l", "racute": "r"}


@pytest.mark.parametrize("ch,base", [("í", "dotlessi"), ("ï", "dotlessi"),
                                     ("ì", "dotlessi"), ("ĩ", "dotlessi"),
                                     ("ĵ", "dotlessj"), ("ĺ", "l"), ("ľ", "l"),
                                     ("ŕ", "r"), ("ř", "r")])
def test_accented_follow_redesigned_base(font, ch, base):
    """La lettre accentuée reprend la base redessinée ; elle peut glisser à
    gauche pour laisser la place à un accent latéral (ľ en gras), sans
    approcher le bord de la cellule à moins de MARGIN/2."""
    g = glyph_contours(font, font.getBestCmap()[ord(ch)])
    dx = split_accent(g, glyph_contours(font, base))[1]
    assert dx is not None and dx <= 0
    assert min(x for c in g for x, _ in c) >= config.MARGIN / 2


@pytest.mark.parametrize("ch,base", [("í", "dotlessi"), ("ï", "dotlessi"),
                                     ("ĵ", "dotlessj"), ("ľ", "l"), ("ŀ", "l"),
                                     ("ļ", "l"), ("ř", "r")])
def test_accent_contours_kept(font, source, ch, base):
    """L'accent garde le même nombre de contours que dans la source."""
    name = font.getBestCmap()[ord(ch)]
    mono = split_accent(glyph_contours(font, name), glyph_contours(font, base))[0]
    orig = split_accent(glyph_contours(source, name), glyph_contours(source, base))[0]
    assert len(mono) == len(orig) > 0


def test_split_accent_tolerates_off_by_one():
    """Luciole Bold : le fût de ï est à y −1..544 au lieu de 0..545."""
    base = [[(80, 0), (280, 0), (280, 545), (80, 545)]]
    acc = [[(80, -1), (280, -1), (280, 544), (80, 544)], [(100, 700), (200, 700), (150, 800)]]
    accent, dx = split_accent(acc, base)
    assert dx == 0 and accent == [acc[1]]


def _body_stem(ttfont, ch):
    """Épaisseur des traits du plus grand morceau d'encre (la lettre sans
    son accent)."""
    from lib.scanline import ink_groups, median_stem
    glyf = ttfont["glyf"]
    coords, ends, flags = glyf[ttfont.getBestCmap()[ord(ch)]].getCoordinates(glyf)
    contours, start = [], 0
    for end in ends:
        contours.append([(coords[j][0], coords[j][1], bool(flags[j] & 1))
                         for j in range(start, end + 1)])
        start = end + 1
    def area(g):
        xs = [p[0] for i in g for p in contours[i]]
        ys = [p[1] for i in g for p in contours[i]]
        return (max(xs) - min(xs)) * (max(ys) - min(ys))
    body = max(ink_groups(contours), key=area)
    return median_stem([contours[i] for i in body])


def _accented_pairs():
    import unicodedata
    from fontTools.ttLib import TTFont
    cmap = TTFont(config.SOURCE).getBestCmap()
    pairs = []
    for code in sorted(cmap):
        parts = unicodedata.decomposition(chr(code)).split()
        if not parts or parts[0].startswith("<"):
            continue
        base = int(parts[0], 16)
        if base in cmap and chr(base) not in "ijlrıȷ" and chr(base).isalpha():
            pairs.append((chr(code), chr(base)))
    return pairs


@pytest.mark.parametrize("ch,base", _accented_pairs())
def test_accented_body_as_heavy_as_base(font, source, ch, base):
    """Ã, Ą, ď… : le garde-fou qui sépare les morceaux ne doit pas amaigrir
    toute la lettre (en gras, Ã avait des fûts de 100 contre 250 pour A)."""
    want = _body_stem(source, ch) / _body_stem(source, base)
    got = _body_stem(font, ch) / _body_stem(font, base)
    # 0,8 : dans ď, le caron posé à droite prend de la place, le d est plus
    # compressé que d seul (0,82 en gras)
    assert got >= 0.8 * want, (got, want)
