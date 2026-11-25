"""Italiques : les fontes droites finies, penchées de 15° (Luciole Italic est
une oblique du droit)."""
import math
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

DIST = Path(__file__).resolve().parent.parent / "dist"
ANGLE = 15
Y0 = 385          # Luciole : le n droit commence à 90, l'italique à −13
ITALICS = [("Italic", "Regular", "Italic"),
           ("BoldItalic", "Bold", "Bold Italic")]
CHECKED = ["n", "percent", "i", "l", "zero", "m", "O"]


@pytest.fixture(scope="module", params=ITALICS, ids=[i[0] for i in ITALICS])
def pair(request):
    ps, upright, style = request.param
    return (TTFont(DIST / f"LucioleMono-{ps}.ttf"),
            TTFont(DIST / f"LucioleMono-{upright}.ttf"), ps, style)


def _points(font, name):
    glyf = font["glyf"]
    coords, ends, flags = glyf[name].getCoordinates(glyf)
    return list(coords), list(ends), [f & 1 for f in flags]


@pytest.mark.parametrize("name", CHECKED)
def test_points_are_slanted_upright(pair, name):
    ital, up, *_ = pair
    t = math.tan(math.radians(ANGLE))
    coords, ends, flags = _points(up, name)
    expected = [(round(x + (y - Y0) * t), y) for x, y in coords]
    assert _points(ital, name) == (expected, ends, flags)


def test_same_advances_and_cmap(pair):
    ital, up, *_ = pair
    assert ital.getGlyphOrder() == up.getGlyphOrder()
    for name in up.getGlyphOrder():
        assert ital["hmtx"][name][0] == up["hmtx"][name][0], name
    assert ital.getBestCmap() == up.getBestCmap()


def test_lsb_is_xmin(pair):
    ital = pair[0]
    ital["glyf"].compile(ital)  # recalcule les boîtes
    for name in ital.getGlyphOrder():
        g = ital["glyf"][name]
        if g.numberOfContours:
            assert ital["hmtx"][name][1] == g.xMin, name


def test_italic_flags(pair):
    ital, up, *_ = pair
    assert ital["post"].italicAngle == -ANGLE
    assert ital["post"].isFixedPitch == 1
    sel = ital["OS/2"].fsSelection
    assert sel & 1 and not sel & 64
    assert bool(sel & 32) == bool(up["OS/2"].fsSelection & 32)   # BOLD gardé
    assert ital["head"].macStyle & 2
    hhea = ital["hhea"]
    run = hhea.caretSlopeRun / hhea.caretSlopeRise
    assert abs(run - math.tan(math.radians(ANGLE))) < 0.01


def test_names(pair):
    ital, _, ps, style = pair
    n = ital["name"]
    assert n.getDebugName(1) == n.getDebugName(16) == "Luciole Mono"
    assert n.getDebugName(2) == n.getDebugName(17) == style
    assert n.getDebugName(4) == f"Luciole Mono {style}"
    assert n.getDebugName(6) == f"LucioleMono-{ps}"
    assert "Bourcellier" in n.getDebugName(13)
