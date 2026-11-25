import pytest

from lib.accents import glyph_contours


def _bbox(contour):
    xs, ys = [p[0] for p in contour], [p[1] for p in contour]
    return min(xs), min(ys), max(xs), max(ys)


def _counters(contours):
    """Contours entièrement contenus dans un autre : les trous des anneaux."""
    boxes = [_bbox(c) for c in contours]
    return [a for a in boxes
            if any(b != a and b[0] <= a[0] and b[1] <= a[1] and a[2] <= b[2]
                   and a[3] <= b[3] for b in boxes)]


@pytest.mark.parametrize("name,rings", [("percent", 2), ("perthousand", 3)])
def test_percent_rings_stay_round(font, name, rings):
    """Les anneaux de % et ‰ restent ronds : trous au plus 2,2 fois plus hauts
    que larges (1,6 dans la source), au lieu d'ellipses écrasées."""
    counters = _counters(glyph_contours(font, name))
    assert len(counters) == rings
    for x0, y0, x1, y1 in counters:
        assert (y1 - y0) / (x1 - x0) <= 2.2, (x0, y0, x1, y1)
