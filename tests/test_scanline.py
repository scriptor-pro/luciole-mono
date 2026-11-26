from lib.scanline import median_gap


def _rect(x0, y0, x1, y1):
    return [(x0, y0, True), (x0, y1, True), (x1, y1, True), (x1, y0, True)]


def test_two_stems_gap():
    """Deux fûts séparés de 100 : l'espace intérieur médian vaut 100."""
    assert median_gap([_rect(0, 0, 100, 500), _rect(200, 0, 300, 500)]) == 100


def test_single_stem_has_no_gap():
    assert median_gap([_rect(0, 0, 100, 500)]) is None


def test_quadratic_ring_gap():
    """Anneau carré à coins arrondis (points hors courbe implicites) : le trou
    fait 100 de large au milieu."""
    outer = [(0, 50, True), (0, 0, False), (50, 0, True), (250, 0, True), (300, 0, False),
             (300, 50, True), (300, 450, True), (300, 500, False), (250, 500, True),
             (50, 500, True), (0, 500, False), (0, 450, True)]
    inner = _rect(100, 100, 200, 400)
    assert median_gap([outer, inner]) == 100


def test_median_stem_of_two_stems():
    """Deux fûts de 100 et 60 sur toute la hauteur : trait le plus fin = 60."""
    from lib.scanline import median_stem
    assert median_stem([_rect(0, 0, 100, 500), _rect(200, 0, 260, 500)]) == 60


def test_median_stem_ignores_short_bar():
    """Un T : la barre horizontale (haut) ne change pas la médiane du fût."""
    from lib.scanline import median_stem
    t = [(0, 400, True), (0, 500, True), (300, 500, True), (300, 400, True),
         (190, 400, True), (190, 0, True), (110, 0, True), (110, 400, True)]
    assert median_stem([t]) == 80


def test_gap_percentile_on_wedge():
    """Deux traits obliques : l'espace va de 80 en bas à 280 en haut ; la
    médiane vaut ~180, le 75e centile ~230."""
    from lib.scanline import median_gap
    left = [(0, 400, True), (60, 400, True), (160, 0, True), (100, 0, True)]
    right = [(340, 400, True), (400, 400, True), (300, 0, True), (240, 0, True)]
    assert 170 <= median_gap([left, right]) <= 190
    assert 220 <= median_gap([left, right], q=0.75) <= 240


def test_gap_rows_counts_every_gap_wide_enough():
    from lib.scanline import gap_rows
    two_gaps = [_rect(0, 0, 10, 100), _rect(30, 0, 40, 100), _rect(45, 0, 55, 100)]
    assert gap_rows(two_gaps, 10) == 39          # seul l'espace de 20 compte
    assert gap_rows(two_gaps, 4) == 2 * 39
    assert gap_rows(two_gaps, 10, sx=0.4) == 0   # 20 × 0,4 = 8 < 10


def test_min_distance_between_shapes():
    from lib.scanline import min_distance
    a = [_rect(0, 0, 100, 100)]
    assert min_distance(a, [_rect(130, 0, 200, 100)]) == 30          # côte à côte
    assert min_distance(a, [_rect(130, 140, 200, 200)]) == 50        # en diagonale
    assert min_distance(a, [_rect(50, 50, 150, 150)]) == 0           # chevauchement


def test_ink_groups_keeps_holes_with_their_shape():
    from lib.scanline import ink_groups
    o_outer, o_inner = _rect(0, 0, 100, 100), _rect(30, 30, 70, 70)
    dot1, dot2 = _rect(10, 150, 30, 170), _rect(60, 150, 80, 170)
    groups = ink_groups([dot1, o_outer, dot2, o_inner])
    assert sorted(sorted(g) for g in groups) == [[0], [1, 3], [2]]


def test_ink_groups_separates_nested_chevrons():
    """Les boîtes des deux chevrons de « se recouvrent, pas leur encre."""
    from lib.scanline import ink_groups
    def chevron(x):
        return [(x, 50, True), (x + 40, 100, True), (x + 60, 100, True),
                (x + 20, 50, True), (x + 60, 0, True), (x + 40, 0, True)]
    assert len(ink_groups([chevron(0), chevron(30)])) == 2
