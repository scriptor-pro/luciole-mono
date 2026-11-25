"""Opérations de contour partagées (FontForge)."""
import math

import psMat


def embolden(glyph, delta, horizontal=False):
    """Épaissit chaque trait de delta (delta/2 de chaque côté) avec une plume
    ronde à jointures en onglet (angles vifs conservés), puis ramène le glyphe
    à sa hauteur d'origine pour garder ligne de base et hauteur d'x.

    horizontal=True : plume plate horizontale, qui n'épaissit que dans le sens
    de la largeur, exactement là où une compression horizontale a aminci."""
    if horizontal:
        _widen(glyph, delta)
        return
    _, ymin, _, ymax = glyph.boundingBox()
    outline = glyph.foreground.dup()
    glyph.stroke("circular", delta, "butt", "miter")
    for contour in outline:
        glyph.foreground += contour
    glyph.removeOverlap()
    _, ymin2, _, ymax2 = glyph.boundingBox()
    sy = (ymax - ymin) / (ymax2 - ymin2)
    glyph.transform(psMat.compose(psMat.translate(0, -ymin2),
                                  psMat.compose(psMat.scale(1, sy), psMat.translate(0, ymin))))


STEP = 25     # écart maximal entre deux copies : plus fin que tout trait


def _widen(glyph, delta):
    """Somme de Minkowski par un segment horizontal de longueur delta : union
    de copies décalées de −delta/2 à +delta/2, tous les STEP au plus. Garde
    l'orientation des contours ; ne touche pas aux hauteurs."""
    original = glyph.foreground.dup()
    n = max(2, math.ceil(delta / STEP)) + 1
    layer = original.dup()
    layer.transform(psMat.translate(-delta / 2, 0))
    for i in range(1, n):
        copy = original.dup()
        copy.transform(psMat.translate(-delta / 2 + delta * i / (n - 1), 0))
        layer += copy
    glyph.foreground = layer
    glyph.removeOverlap()
