"""% et ‰ redessinés pour la cellule (FontForge).

Le % de Luciole fait 1240 unités : comprimé, ses anneaux deviennent des
ellipses étroites qui forment une tache en petite taille. On réduit plutôt
les anneaux dans les deux sens (ils restent ronds), on les place en haut à
gauche et en bas à droite, et on garde la barre oblique au centre."""
import fontforge
import psMat

from lib.outline import embolden

REDESIGNED = ("percent", "perthousand")

# nom → (échelle des anneaux, épaississement des anneaux,
#        [(indices des contours d'un anneau, (x gauche, y haut))],
#        indice de la barre, échelle horizontale de la barre, centre de la barre)
LAYOUTS = {
    "percent": (0.56, 40, [((0, 2), (40, 770)), ((3, 4), (350, 271))], 1, 0.72, 310),
    # ‰ : barre à gauche pour laisser passer les deux anneaux du bas
    "perthousand": (0.4, 30, [((0, 2), (20, 770)), ((3, 5), (205, 220)),
                              ((4, 6), (400, 220))], 1, 0.6, 190),
}
BAR_EMBOLDEN = 14


def _layer(contours=()):
    layer = fontforge.layer()
    layer.is_quadratic = True
    for c in contours:
        layer += c.dup()
    return layer


def redesign_percents(font, cell):
    for name, (scale, ring_bold, rings, bar_index, bar_scale, bar_center) in LAYOUTS.items():
        glyph = font[name]
        orig = list(glyph.foreground)
        parts = _layer()
        for indices, (left, top) in rings:
            ring = _layer(orig[i] for i in indices)
            ring.transform(psMat.scale(scale, scale))
            x0, _, _, y1 = ring.boundingBox()
            ring.transform(psMat.translate(left - x0, top - y1))
            for c in ring:
                parts += c
        bar = _layer([orig[bar_index]])
        bar.transform(psMat.scale(bar_scale, 1))
        x0, _, x1, _ = bar.boundingBox()
        bar.transform(psMat.translate(bar_center - (x0 + x1) / 2, 0))
        glyph.foreground = parts
        embolden(glyph, ring_bold)
        for c in bar:
            glyph.foreground += c
        embolden(glyph, BAR_EMBOLDEN)
        glyph.removeOverlap()
        x0, _, x1, _ = glyph.boundingBox()
        glyph.transform(psMat.translate((cell - (x1 - x0)) / 2 - x0, 0))
        glyph.correctDirection()
        glyph.round()
        glyph.width = cell
