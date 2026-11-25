"""Opérations de contour partagées (FontForge)."""
import psMat


def embolden(glyph, delta):
    """Épaissit chaque trait de delta (delta/2 de chaque côté) avec une plume
    ronde à jointures en onglet (angles vifs conservés), puis ramène le glyphe
    à sa hauteur d'origine pour garder ligne de base et hauteur d'x."""
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
