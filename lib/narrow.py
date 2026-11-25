"""Redessin des lettres étroites (FontForge), en coordonnées de cellule.

Toutes les dimensions viennent de lib.geometry.measure (g) : le même dessin
s'applique à chaque graisse. Chaque redesign_* renvoie le centre du nouveau
fût, dont dépend la reconstruction des lettres accentuées."""
import fontforge
import psMat

SERIF = 124       # longueur de l'empattement d'attaque au-delà du fût
FOOT = 144        # débord du pied de i de chaque côté du fût
J_CENTER = 396    # centre du fût de ȷ (crochet élargi à gauche)
L_CENTER = 270    # centre du fût de l (queue à droite)
R_CENTER = 230    # centre du fût de r (bras à droite)


def old_stem_center(g):
    """Centre du fût de ı, ȷ, l, r dans la source."""
    return g["stem_left"] + g["stem"] / 2


def _rect(pen, x0, y0, x1, y1):
    pen.moveTo((x0, y0))
    pen.lineTo((x0, y1))
    pen.lineTo((x1, y1))
    pen.lineTo((x1, y0))
    pen.closePath()


def add_serif(glyph, x_from, x_to, y, thickness):
    """Ajoute un rectangle [x_from, x_to] × [y, y + thickness] et fusionne."""
    _rect(glyph.glyphPen(replace=False), x_from, y, x_to, y + thickness)
    glyph.removeOverlap()


def _finish(glyph, cell):
    glyph.removeOverlap()
    glyph.correctDirection()
    glyph.round()
    glyph.width = cell


def _with_dot(font, dotted, dotless, dx, g, cell):
    """dotted = dotless redessiné + point d'origine (au-dessus de x) décalé."""
    dot = [c.dup() for c in font[dotted].foreground if c.boundingBox()[1] > g["xh"]]
    layer = font[dotless].foreground.dup()
    for contour in dot:
        contour.transform(psMat.translate(dx, 0))
        layer += contour
    font[dotted].foreground = layer
    _finish(font[dotted], cell)


def redesign_i(font, g, cell):
    """ı : fût centré, attaque à gauche, pied ; i = ı + point."""
    stem, bar, xh = g["stem"], g["bar"], g["xh"]
    x0 = (cell - stem) // 2
    glyph = font["dotlessi"]
    _rect(glyph.glyphPen(), x0, 0, x0 + stem, xh)
    add_serif(glyph, x0 - SERIF, x0 + stem, xh - bar, bar)
    half = stem // 2 + FOOT
    add_serif(glyph, cell // 2 - half, cell // 2 + half, 0, bar)
    _finish(glyph, cell)
    _with_dot(font, "i", "dotlessi", x0 - g["stem_left"], g, cell)
    return x0 + stem / 2


def redesign_l(font, g, cell):
    """l : bas du t (fût et queue courbe), fût prolongé jusqu'à l'ascendante,
    attaque à gauche."""
    left, right = g["t_stem"]
    dx = L_CENTER - (left + right) / 2
    glyph = font["l"]
    layer = font["t"].foreground.dup()
    layer.transform(psMat.translate(dx, 0))
    glyph.foreground = layer
    _rect(glyph.glyphPen(replace=False), -1000, -1000, 2000, g["t_bar_bottom"])
    glyph.intersect()                       # ne garde que le t sous sa barre
    left, right = left + dx, right + dx
    add_serif(glyph, left, right, g["t_bar_bottom"] - 1,
              g["asc"] - g["t_bar_bottom"] + 1)
    add_serif(glyph, left - SERIF, right, g["asc"] - g["bar"], g["bar"])
    _finish(glyph, cell)
    return L_CENTER


def redesign_j(font, g, cell):
    """ȷ : crochet élargi vers la gauche, attaque à gauche ; j = ȷ + point."""
    left, stem = g["stem_left"], g["stem"]
    dx = J_CENTER - stem / 2 - left
    glyph = font["dotlessj"]
    stretch = psMat.compose(psMat.translate(-left, 0),
                            psMat.compose(psMat.scale(1.6, 1), psMat.translate(left, 0)))
    layer = glyph.foreground
    for contour in layer:
        for point in contour:
            if point.x < left:
                point.transform(stretch)
    glyph.foreground = layer
    glyph.transform(psMat.translate(dx, 0))
    add_serif(glyph, left + dx - SERIF, left + dx + stem, g["xh"] - g["bar"], g["bar"])
    _finish(glyph, cell)
    _with_dot(font, "j", "dotlessj", dx, g, cell)
    return J_CENTER


def redesign_r(font, g, cell):
    """r : décalé, pied horizontal sous le fût (plus long côté bras)."""
    stem = g["stem"]
    glyph = font["r"]
    glyph.transform(psMat.translate(R_CENTER - stem / 2 - g["stem_left"], 0))
    add_serif(glyph, R_CENTER - (stem // 2 + 84), R_CENTER + (stem // 2 + 104), 0, g["bar"])
    _finish(glyph, cell)
    return R_CENTER


def slashed_zero(font):
    """Le zéro barré d'origine (feature zero) devient le zéro par défaut."""
    for name in list(font):
        if name.startswith("zero.slash"):
            suffix = name[len("zero.slash"):]          # "", "LP", "osf"…
            target = "zero" + ("." + suffix if suffix else "")
            if target in font:
                font[target].foreground = font[name].foreground.dup()
