import os

import pytest
from fontTools.ttLib import TTFont

import config
from conftest import DIST
from lib.scanline import gap_rows, median_gap, median_stem
from render import render
from stroke import holes

WEIGHED = list("mwMW@Œ½¼¾™№") + ["⇔", "→"]
WIDE = WEIGHED + ["%", "‰"]
CMAP = TTFont(config.SOURCE).getBestCmap()
# Un espace blanc se voit de la même façon quelle que soit la graisse des
# traits qui l'entourent : seuil absolu (0,15 × fût du Regular).
MIN_VISIBLE_GAP = 17
# Morceaux très proches (chiffres et barre de fraction, N et º) : l'écart
# minimal entre morceaux (config.SEPARATION) limite leur épaississement.
SEPARATED = set("½¼¾№")
REGULAR = os.path.join(os.path.dirname(DIST), "LucioleMono-Regular.ttf")


def _present(chars):
    return [c for c in chars if ord(c) in CMAP]


def _flagged(ttfont, ch):
    glyf = ttfont["glyf"]
    g = glyf[ttfont.getBestCmap()[ord(ch)]]
    coords, ends, flags = g.getCoordinates(glyf)
    contours, start = [], 0
    for end in ends:
        contours.append([(coords[j][0], coords[j][1], bool(flags[j] & 1))
                         for j in range(start, end + 1)])
        start = end + 1
    return contours


def _ink_width(contours):
    xs = [p[0] for c in contours for p in c]
    return max(xs) - min(xs)


@pytest.mark.skipif(config.STYLE != "Regular", reason="le gras ne tient pas "
                    "dans la cellule : voir test_bold_heavier_than_regular")
@pytest.mark.parametrize("ch", _present(WIDE))
def test_wide_glyph_stems_keep_weight(font, source, ch):
    """Un glyphe compressé garde l'épaisseur horizontale de ses traits
    (médiane par balayage) : entre 70 % et 130 % de la source."""
    ratio = median_stem(_flagged(font, ch)) / median_stem(_flagged(source, ch))
    low = 0.6 if ch in SEPARATED else 0.7
    assert low <= ratio <= 1.3, ratio


def _ink(path, ch):
    return sum(p < 128 for p in render(path, ch, 100).tobytes())


# ½ ¾ ¼ ™ № ⇔ → : rares, sans place pour s'épaissir (les flèches ont la même
# graisse dans les deux sources)
BOLD_CHECKED = list("m@Œ&#noaeHO0")
# Le gras est un demi-gras (fûts 156). M, W, w : leurs encoches étroites ne
# laissent pas la place d'épaissir sans les boucher
# (test_wide_glyph_keeps_its_gaps) ; % et ‰ : l'épaisseur de leurs anneaux
# est bornée par la contreforme minimale (lib/symbols.py). Ils restent au
# moins aussi noirs que le regular.
BOLD_LIGHT = list("MWw%‰")


@pytest.mark.skipif(config.STYLE != "Bold", reason="gras seulement")
@pytest.mark.parametrize("ch", _present(BOLD_CHECKED))
def test_bold_heavier_than_regular(ch):
    """Le gras reste visiblement plus noir que le regular, glyphe par glyphe
    (au moins 10 % d'encre en plus)."""
    assert _ink(DIST, ch) >= 1.10 * _ink(REGULAR, ch)


@pytest.mark.skipif(config.STYLE != "Bold", reason="gras seulement")
@pytest.mark.parametrize("ch", _present(BOLD_LIGHT))
def test_bold_light_glyphs_not_lighter_than_regular(ch):
    assert _ink(DIST, ch) >= _ink(REGULAR, ch)


@pytest.mark.parametrize("ch", _present(WIDE))
def test_wide_glyph_not_blob(font, source, ch):
    """L'épaississement ne referme pas les espaces intérieurs : l'espace
    médian reste ≥ MIN_VISIBLE_GAP, ou au moins 90 % de ce que donnerait une
    simple mise à l'échelle de la source."""
    mono, src = _flagged(font, ch), _flagged(source, ch)
    gap, src_gap = median_gap(mono), median_gap(src)
    if gap is None or src_gap is None:
        return
    scaled = src_gap * _ink_width(mono) / _ink_width(src)
    assert gap >= min(MIN_VISIBLE_GAP, 0.9 * scaled), (gap, scaled)


@pytest.mark.parametrize("ch", _present(WIDE))
def test_wide_glyph_counters_stay_open(ch):
    """L'épaississement ne bouche aucune contreforme."""
    assert holes(DIST, ch) >= holes(config.SOURCE, ch)


# Part des espaces blancs (ligne de balayage × espace) que l'épaississement
# doit laisser visibles, par rapport à la source simplement réduite. En
# Regular, les glyphes bien lisibles gardent ≥ 0,57 ; le M gras bouché, 0,24.
# % et ‰ exclus : leurs anneaux sont réduits exprès (lib/symbols.py).
KEEP_GAPS = 0.5


@pytest.mark.parametrize("ch", _present(WEIGHED))
def test_wide_glyph_keeps_its_gaps(font, source, ch):
    """Aucun espace blanc ne disparaît en masse : les encoches étroites
    (bas du M) comptent autant que les grandes."""
    mono, src = _flagged(font, ch), _flagged(source, ch)
    sx = _ink_width(mono) / _ink_width(src)
    assert gap_rows(mono, MIN_VISIBLE_GAP) >= \
        KEEP_GAPS * gap_rows(src, MIN_VISIBLE_GAP, sx=sx)
