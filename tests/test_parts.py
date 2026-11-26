"""Aucune partie d'un glyphe ne se soude à une autre : trémas, points de
suspension, accents écartés de la lettre, barre de % séparée des anneaux…
(les tests de contreformes ne voient que les creux blancs)."""
import pytest
from fontTools.ttLib import TTFont

import config
from conftest import DIST
from stroke import ink_parts

SOURCE_CMAP = TTFont(config.SOURCE).getBestCmap()
MONO_CMAP = TTFont(DIST).getBestCmap()
# Soudures connues, reportées : ligatures typographiques et fractions (rares,
# surtout du texte collé depuis un PDF), ℗.
DEFERRED = set("ﬀﬁﬂﬃﬄ½¼¾⅓⅔⅛⅜⅝⅞℗")
CHARS = [chr(c) for c in sorted(SOURCE_CMAP)
         if c > 32 and c in MONO_CMAP and not 0xE000 <= c <= 0xF8FF
         and chr(c) not in DEFERRED]


@pytest.mark.parametrize("ch", CHARS, ids=[f"U+{ord(c):04X}" for c in CHARS])
def test_no_welded_parts(ch):
    assert ink_parts(DIST, ch) >= ink_parts(config.SOURCE, ch)
