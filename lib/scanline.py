"""Largeur typique des espaces intérieurs d'un glyphe, par balayage.

Un contour est une liste de points (x, y, sur_la_courbe) au format TrueType
quadratique : entre deux points hors courbe consécutifs, un point sur la
courbe est implicite au milieu."""
import statistics

STEPS = 8          # segments par arc quadratique
SCANS = 40         # lignes de balayage


def _flatten(contour):
    """Polyligne fermée approchant le contour."""
    pts = list(contour)
    # points sur la courbe implicites entre deux points hors courbe
    full = []
    for a, b in zip(pts, pts[1:] + pts[:1]):
        full.append(a)
        if not a[2] and not b[2]:
            full.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, True))
    start = next(i for i, p in enumerate(full) if p[2])
    full = full[start:] + full[:start + 1]          # fermé, débute sur la courbe
    out, i = [full[0][:2]], 1
    while i < len(full):
        p = full[i]
        if p[2]:
            out.append(p[:2])
            i += 1
            continue
        p0, end = out[-1], full[i + 1][:2]
        for k in range(1, STEPS + 1):
            t = k / STEPS
            out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p[0] + t * t * end[0],
                        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p[1] + t * t * end[1]))
        i += 2
    return out[:-1]


def _segments(contours):
    for contour in contours:
        poly = _flatten(contour)
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if a[1] != b[1]:
                yield a, b


def _scan(contours):
    """Pour chaque ligne de balayage : liste triée des abscisses de croisement."""
    segs = list(_segments(contours))
    if not segs:
        return []
    ys = [p[1] for s in segs for p in s]
    y0, y1 = min(ys), max(ys)
    rows = []
    for k in range(1, SCANS):
        y = y0 + (y1 - y0) * k / SCANS + 0.01
        rows.append(sorted(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
                           for a, b in segs if min(a[1], b[1]) <= y < max(a[1], b[1])))
    return rows


def median_gap(contours, q=0.5):
    """Centile q (médiane par défaut), sur les lignes de balayage, du plus
    petit espace blanc entre deux zones d'encre ; None si le glyphe n'en a
    pas (un seul fût)."""
    gaps = []
    for xs in _scan(contours):
        inner = [xs[j + 1] - xs[j] for j in range(1, len(xs) - 1, 2)]
        if inner:
            gaps.append(min(inner))
    if not gaps:
        return None
    gaps.sort()
    return round(gaps[min(len(gaps) - 1, int(q * len(gaps)))]) if q != 0.5 \
        else round(statistics.median(gaps))


def median_stem(contours):
    """Médiane, sur les lignes de balayage, de la plus fine zone d'encre :
    l'épaisseur horizontale typique des traits du glyphe."""
    runs = [min(xs[j + 1] - xs[j] for j in range(0, len(xs) - 1, 2))
            for xs in _scan(contours) if len(xs) >= 2]
    return round(statistics.median(runs)) if runs else None


def gap_rows(contours, min_width, sx=1.0):
    """Nombre de couples (ligne de balayage, espace blanc intérieur) dont la
    largeur, multipliée par sx, atteint min_width. Contrairement à un
    centile, une encoche étroite qui se bouche fait baisser le compte."""
    return sum(1 for xs in _scan(contours)
               for j in range(1, len(xs) - 1, 2)
               if (xs[j + 1] - xs[j]) * sx >= min_width)


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = 0 if dx == dy == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy)
                                              / (dx * dx + dy * dy)))
    return ((p[0] - a[0] - t * dx) ** 2 + (p[1] - a[1] - t * dy) ** 2) ** 0.5


def _cross(a, b, c, d):
    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return side(a, b, c) * side(a, b, d) < 0 and side(c, d, a) * side(c, d, b) < 0


def _inside(p, polys):
    inside = False
    for poly in polys:
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if (a[1] > p[1]) != (b[1] > p[1]) and \
                    p[0] < a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                inside = not inside
    return inside


def min_distance(contours_a, contours_b):
    """Plus petite distance entre l'encre de deux groupes de contours
    (0 s'ils se touchent ou se chevauchent)."""
    pa = [_flatten(c) for c in contours_a]
    pb = [_flatten(c) for c in contours_b]
    edges = lambda polys: [(a, b) for poly in polys for a, b in zip(poly, poly[1:] + poly[:1])]
    ea, eb = edges(pa), edges(pb)
    if any(_cross(a, b, c, d) for a, b in ea for c, d in eb) \
            or _inside(pa[0][0], pb) or _inside(pb[0][0], pa):
        return 0
    return round(min(min(_seg_dist(p, c, d) for poly in pa for p in poly for c, d in eb),
                     min(_seg_dist(p, a, b) for poly in pb for p in poly for a, b in ea)))


def _bbox(contour):
    xs = [p[0] for p in contour]
    ys = [p[1] for p in contour]
    return min(xs), min(ys), max(xs), max(ys)


def ink_groups(contours):
    """Indices des contours regroupés par morceau d'encre : deux contours qui
    se touchent, ou dont l'un contient l'autre (un trou et sa forme), vont
    ensemble. Les boîtes ne servent que de filtre : celles des chevrons de «
    se recouvrent sans que leur encre se touche."""
    boxes = [_bbox(c) for c in contours]
    parent = list(range(len(contours)))

    def root(i):
        while parent[i] != i:
            i = parent[i]
        return i
    for i, a in enumerate(boxes):
        for j in range(i + 1, len(boxes)):
            b = boxes[j]
            if a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3] \
                    and min_distance([contours[i]], [contours[j]]) == 0:
                parent[root(i)] = root(j)
    out = {}
    for i in range(len(contours)):
        out.setdefault(root(i), []).append(i)
    return list(out.values())
