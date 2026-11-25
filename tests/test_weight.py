import pytest

import config
from conftest import DIST
from stroke import holes, stroke_survival

# % et ‰ : anneaux trop étroits pour la mesure par érosion (contrôle visuel)
WEIGHED = list("mwMW@Œ½¼¾™№") + ["⇔", "→"]
WIDE = WEIGHED + ["%", "‰"]


@pytest.mark.parametrize("ch", WEIGHED)
def test_wide_glyph_stems_keep_weight(ch):
    """Les traits d'un glyphe compressé gardent leur épaisseur, quel que soit
    leur angle, sans devenir gras : entre 70 % et 160 % de la résistance à
    l'érosion de la source."""
    ratio = stroke_survival(DIST, ch) / stroke_survival(config.SOURCE, ch)
    assert 0.7 <= ratio <= 1.6, ratio


@pytest.mark.parametrize("ch", WIDE)
def test_wide_glyph_counters_stay_open(ch):
    """L'épaississement ne bouche aucune contreforme."""
    assert holes(DIST, ch) >= holes(config.SOURCE, ch)
