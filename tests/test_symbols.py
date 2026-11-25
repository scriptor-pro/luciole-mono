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


def _ratios(ttfont, name):
    return [(y1 - y0) / (x1 - x0) for x0, y0, x1, y1 in _counters(glyph_contours(ttfont, name))]


@pytest.mark.parametrize("name,rings", [("percent", 2), ("perthousand", 3)])
def test_percent_rings_stay_round(font, source, name, rings):
    """Les anneaux de % et ‰ restent ronds : trous au plus 1,35 fois plus
    allongés que dans la source (1,62 en Regular → 2,2 ; 2,18 en gras),
    au lieu d'ellipses écrasées (environ 5 avant redessin)."""
    mono, src = _ratios(font, name), _ratios(source, name)
    assert len(mono) == rings
    assert max(mono) <= 1.35 * max(src), (mono, src)


def test_ring_scale_regular_percent():
    """Anneau du % Regular (410 de large, trou 198) → 270 de large, paroi 98,6 :
    s·W + e = 270 et s·paroi + e = 98,6."""
    from lib.symbols import ring_scale
    s, e = ring_scale(410, 198, 270, 98.56)
    assert abs(s * 410 + e - 270) < 0.01
    assert abs(s * 106 + e - 98.56) < 0.01
