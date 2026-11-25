import os

import pytest
from fontTools.ttLib import TTFont

from lib.geometry import measure

DIR = os.path.expanduser("~/.local/share/fonts/typographies.fr/TrueType/Luciole")


@pytest.mark.parametrize("style,expected", [
    ("Regular", dict(stem=112, stem_left=90, xh=545, asc=791, bar=96,
                     t_stem=(118, 230), t_bar_bottom=449)),
    ("Bold", dict(stem=200, stem_left=80, xh=545, asc=791, bar=150,
                  t_stem=(108, 308), t_bar_bottom=395)),
])
def test_measure(style, expected):
    assert measure(TTFont(f"{DIR}/Luciole_{style}.ttf")) == expected
