"""Redessin des lettres étroites (FontForge), en coordonnées de cellule (620).

Mesures de Luciole Regular : fût 112, barre du t 96, hauteur d'x 545,
ascendante 791. Les glyphes produits ici ne sont pas recentrés ensuite."""
import psMat

BAR = 96          # épaisseur des empattements = barre horizontale du t
SERIF = 124       # longueur de l'empattement d'attaque au-delà du fût
XH, ASC = 545, 791
OLD_STEM_CENTER = 146     # centre du fût de ı, ȷ, l, r dans la source (90–202)
# centre du fût après redessin (doit suivre les fonctions redesign_*)
STEM_CENTER = {"dotlessi": 310, "dotlessj": 396, "l": 270, "r": 230}


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


def _dot(font, name):
    """Contours au-dessus de la hauteur d'x (le point de i ou j)."""
    return [c.dup() for c in font[name].foreground if c.boundingBox()[1] > XH]


def _with_dot(font, dotted, dotless, dx, cell):
    """dotted = dotless redessiné + point d'origine décalé de dx."""
    dot = _dot(font, dotted)
    layer = font[dotless].foreground.dup()
    for contour in dot:
        contour.transform(psMat.translate(dx, 0))
        layer += contour
    font[dotted].foreground = layer
    _finish(font[dotted], cell)


def redesign_i(font, stem, cell):
    """ı : fût centré, attaque à gauche, pied ; i = ı + point."""
    x0 = (cell - stem) // 2                      # 254
    g = font["dotlessi"]
    _rect(g.glyphPen(), x0, 0, x0 + stem, XH)
    add_serif(g, x0 - SERIF, x0 + stem, XH - BAR, BAR)
    add_serif(g, cell // 2 - 200, cell // 2 + 200, 0, BAR)
    _finish(g, cell)
    _with_dot(font, "i", "dotlessi", x0 - 90, cell)   # fût d'origine à x=90


def redesign_l(font, stem, cell):
    """l : attaque à gauche, terminé par la queue courbe du t (décalée)."""
    dx = 96
    g = font["l"]
    pen = g.glyphPen()
    pen.moveTo((393 + dx, 8))
    pen.qCurveTo((371 + dx, -1), (317 + dx, -11), (289 + dx, -11))
    pen.qCurveTo((203 + dx, -11), (118 + dx, 85), (118 + dx, 181))
    pen.lineTo((118 + dx, ASC - BAR))
    pen.lineTo((118 + dx - SERIF, ASC - BAR))
    pen.lineTo((118 + dx - SERIF, ASC))
    pen.lineTo((230 + dx, ASC))
    pen.lineTo((230 + dx, 243))
    pen.qCurveTo((230 + dx, 154), (265 + dx, 90), (313 + dx, 90))
    pen.qCurveTo((332 + dx, 90), (375 + dx, 98), (393 + dx, 104))
    pen.closePath()
    _finish(g, cell)


def redesign_j(font, stem, cell):
    """ȷ : crochet élargi vers la gauche, attaque à gauche ; j = ȷ + point."""
    left = 90                                     # bord gauche du fût dans la source
    dx = 250
    g = font["dotlessj"]
    stretch = psMat.compose(psMat.translate(-left, 0),
                            psMat.compose(psMat.scale(1.6, 1), psMat.translate(left, 0)))
    layer = g.foreground
    for contour in layer:
        for point in contour:
            if point.x < left:
                point.transform(stretch)
    g.foreground = layer
    g.transform(psMat.translate(dx, 0))
    add_serif(g, left + dx - SERIF, left + dx + stem, XH - BAR, BAR)
    _finish(g, cell)
    _with_dot(font, "j", "dotlessj", dx, cell)


def redesign_r(font, stem, cell):
    """r : décalé à droite, pied horizontal centré sur le fût."""
    dx = 84
    g = font["r"]
    g.transform(psMat.translate(dx, 0))
    center = 90 + dx + stem // 2                  # 230
    add_serif(g, center - 140, center + 160, 0, BAR)
    _finish(g, cell)


def slashed_zero(font):
    """Le zéro barré d'origine (feature zero) devient le zéro par défaut."""
    for name in list(font):
        if name.startswith("zero.slash"):
            suffix = name[len("zero.slash"):]          # "", "LP", "osf"…
            target = "zero" + ("." + suffix if suffix else "")
            if target in font:
                font[target].foreground = font[name].foreground.dup()
