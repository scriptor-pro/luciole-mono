import pytest

import config
from conftest import DIST
from render import render


@pytest.mark.parametrize("ch", list("iljrftI1"))
def test_narrow_letters_fill_cell(font, ch):
    g = font["glyf"][font.getBestCmap()[ord(ch)]]
    assert g.xMax - g.xMin >= 0.55 * config.CELL


@pytest.mark.parametrize("a,b", [("l", "1"), ("l", "I"), ("I", "1"), ("l", "|"),
                                 ("I", "|"), ("0", "O"), ("0", "o")])
def test_confusables_differ(a, b):
    ia, ib = render(DIST, a, 32).tobytes(), render(DIST, b, 32).tobytes()
    diff = sum(abs(p - q) > 128 for p, q in zip(ia, ib))
    ink = min(sum(p < 128 for p in ia), sum(p < 128 for p in ib))
    assert diff >= 0.25 * ink


def test_zero_is_slashed(font, source):
    assert font["glyf"]["zero"].numberOfContours == \
        source["glyf"]["zero.slash"].numberOfContours
