"""Le gras de Luciole Mono est un demi-gras dérivé de Luciole Regular
(make_source.py) : fûts à mi-chemin entre Regular (112) et Bold (200)."""
import os

import pytest
from fontTools.ttLib import TTFont

import config
from lib.accents import glyph_contours, split_accent
from lib.geometry import measure

DERIVED = config.STYLE in config.DERIVED
pytestmark = pytest.mark.skipif(not DERIVED, reason="graisse tirée directement de Luciole")


def test_derived_source_stem():
    base, delta = config.DERIVED[config.STYLE]
    geo, orig = measure(TTFont(config.SOURCE)), measure(TTFont(config.ORIGINAL[base]))
    assert geo["stem"] == orig["stem"] + delta
    assert (geo["xh"], geo["asc"]) == (orig["xh"], orig["asc"])   # hauteurs gardées


def test_derived_source_keeps_all_characters():
    base, _ = config.DERIVED[config.STYLE]
    assert set(TTFont(config.SOURCE).getBestCmap()) >= set(TTFont(config.ORIGINAL[base]).getBestCmap())


@pytest.mark.parametrize("ch,base", [("í", "dotlessi"), ("ì", "dotlessi"), ("ĺ", "l"),
                                     ("ŕ", "r"), ("ĵ", "dotlessj")])
def test_derived_accented_contain_their_base(ch, base):
    """Chaque morceau est épaissi à part : la lettre de í reste celle de ı
    (sinon l'accent n'est pas reconstruit sur le i redessiné)."""
    src = TTFont(config.SOURCE)
    name = src.getBestCmap()[ord(ch)]
    assert split_accent(glyph_contours(src, name), glyph_contours(src, base))[1] is not None
