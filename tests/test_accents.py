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
