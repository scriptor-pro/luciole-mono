import pytest

from lib.accents import glyph_contours


@pytest.mark.parametrize("suffix", ["", ".LP", ".LT", ".OP", ".OT", ".osf"])
def test_zero_variants_slashed(font, source, suffix):
    """Le zéro reste barré sous tnum/pnum/lnum/onum."""
    assert font["glyf"]["zero" + suffix].numberOfContours == \
        source["glyf"]["zero.slash" + suffix.lstrip(".")].numberOfContours


def test_turkish_i_redesigned(font):
    """locl tr/az/crh remplace i par idotaccent : même dessin que i."""
    assert glyph_contours(font, "idotaccent") == glyph_contours(font, "i")


@pytest.mark.parametrize("code", [0x00A0, 0x202F])
def test_no_break_spaces_mapped(font, code):
    """Espaces insécables présentes dans toutes les tables Unicode, à 620."""
    for table in font["cmap"].tables:
        if table.isUnicode():
            assert code in table.cmap, (table.platformID, table.platEncID)
    assert font["hmtx"][font.getBestCmap()[code]][0] == 620


def test_no_stale_luciole_names(font):
    for record in font["name"].names:
        text = record.toUnicode()
        if record.nameID not in (0, 13, 14) and "Luciole" in text:
            assert "Mono" in text, (record.nameID, text)
