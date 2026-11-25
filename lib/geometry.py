"""Géométrie de la police source, mesurée (fontTools) plutôt que codée en dur,
pour que le même script serve à toutes les graisses."""


def _points(ttfont, name):
    glyf = ttfont["glyf"]
    return [(round(x), round(y)) for x, y in glyf[name].getCoordinates(glyf)[0]]


def measure(ttfont):
    """Mesures utilisées par le redessin :
    stem, stem_left : épaisseur et bord gauche du fût de ı ;
    xh, asc : hauteur d'x (haut de ı) et ascendante (haut de l) ;
    t_stem : bords du fût de t (points au sommet du t) ;
    t_bar_bottom, bar : bas et épaisseur de la barre du t (bout gauche)."""
    glyf = ttfont["glyf"]
    i, l, t = glyf["dotlessi"], glyf["l"], glyf["t"]
    t_pts = _points(ttfont, "t")
    top = [x for x, y in t_pts if y == t.yMax]
    bar_ys = [y for x, y in t_pts if x == t.xMin]
    return dict(stem=i.xMax - i.xMin, stem_left=i.xMin, xh=i.yMax, asc=l.yMax,
                bar=max(bar_ys) - min(bar_ys), t_stem=(min(top), max(top)),
                t_bar_bottom=min(bar_ys))
