import subprocess

import config
from conftest import DIST

ZERO_WIDTH = ("NULL", ".null")


def test_every_glyph_is_cell_width(font):
    for name in font.getGlyphOrder():
        expected = 0 if name in ZERO_WIDTH else config.CELL
        assert font["hmtx"][name][0] == expected, name


def test_same_codepoints_as_source(font, source):
    """Mêmes caractères que la source, plus les espaces insécables ajoutées."""
    assert set(font.getBestCmap()) - set(source.getBestCmap()) <= {0x00A0, 0x202F}
    assert set(source.getBestCmap()) <= set(font.getBestCmap())


def test_fixed_pitch_metadata(font):
    assert font["post"].isFixedPitch == 1
    assert font["OS/2"].panose.bProportion == 9
    assert font["OS/2"].xAvgCharWidth == config.CELL


def test_names(font):
    n = font["name"]
    assert n.getDebugName(1) == "Luciole Mono"
    assert n.getDebugName(6) == config.PS_NAME
    assert n.getDebugName(2) == config.STYLE
    assert "Bourcellier" in n.getDebugName(13)
    assert "Luciole Mono" in n.getDebugName(13)


def _features(font, table):
    if table not in font:
        return set()
    return {r.FeatureTag for r in font[table].table.FeatureList.FeatureRecord}


def test_no_kern_no_liga(font):
    assert "kern" not in _features(font, "GPOS")
    assert "liga" not in _features(font, "GSUB")


def test_ink_inside_cell(font):
    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.numberOfContours:
            assert g.xMin >= 0 and g.xMax <= config.CELL, name


def test_fontconfig_sees_mono():
    out = subprocess.run(["fc-query", "-f", "%{spacing}\n", DIST],
                         capture_output=True, text=True).stdout
    assert out.split()[0] == "100"
