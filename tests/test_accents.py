import pytest

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
    g = glyph_contours(font, font.getBestCmap()[ord(ch)])
    assert split_accent(g, glyph_contours(font, base))[1] == 0


@pytest.mark.parametrize("ch,base", [("í", "dotlessi"), ("ï", "dotlessi"),
                                     ("ĵ", "dotlessj"), ("ľ", "l"), ("ŀ", "l"),
                                     ("ļ", "l"), ("ř", "r")])
def test_accent_contours_kept(font, source, ch, base):
    """L'accent garde le même nombre de contours que dans la source."""
    name = font.getBestCmap()[ord(ch)]
    mono = split_accent(glyph_contours(font, name), glyph_contours(font, base))[0]
    orig = split_accent(glyph_contours(source, name), glyph_contours(source, base))[0]
    assert len(mono) == len(orig) > 0
