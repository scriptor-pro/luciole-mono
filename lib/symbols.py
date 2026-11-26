"""% et ‰ redessinés pour la cellule (FontForge).

Le % de Luciole est très large : comprimé, ses anneaux deviennent des
ellipses étroites qui forment une tache en petite taille. On réduit plutôt
les anneaux dans les deux sens (ils restent ronds), on les place en haut à
gauche et en bas à droite, et on garde la barre oblique entre les deux.
L'épaisseur des anneaux suit la graisse (1 × fût), dans la limite d'une
contreforme minimale."""
import math

try:
    import fontforge
    import psMat
except ImportError:          # hors FontForge (tests)
    fontforge = psMat = None

try:
    from lib.outline import embolden
except ImportError:          # hors FontForge (tests)
    embolden = None
from lib.scanline import min_distance

REDESIGNED = ("percent", "perthousand")
RING_STROKE = 1.0         # épaisseur visée des anneaux, en fraction du fût
BAR_EMBOLDEN = 0.125     # épaississement de la barre oblique (× fût : 14 en Regular)
COUNTER_PER_STEM = 0.6    # contreforme minimale réduite par unité de fût au-delà de 112
CLEARANCE = 25            # blanc minimal entre barre et anneaux (sinon soudés à petite taille)
BAR_SHEAR_STEP, BAR_SHEAR_MAX = 0.02, 0.3   # cisaillement de la barre tant qu'elle frôle un anneau

# nom → dict(largeur finale d'un anneau, contreforme minimale,
#   anneaux [(indices des contours, "top" ou "bottom", x gauche)],
#   indice de la barre, échelle horizontale de la barre, centre de la barre)
LAYOUTS = {
    "percent": dict(ring_width=270, min_counter=70,
                    rings=[((0, 2), "top", 40), ((3, 4), "bottom", 350)],
                    bar=1, bar_scale=0.72, bar_center=310),
    # ‰ : barre à gauche pour laisser passer les deux anneaux du bas
    # (anneaux du bas : 190–370 et 410–590, 40 d'écart)
    "perthousand": dict(ring_width=180, min_counter=50,
                        rings=[((0, 2), "top", 20), ((3, 5), "bottom", 190),
                               ((4, 6), "bottom", 410)],
                        bar=1, bar_scale=0.6, bar_center=190),
}


def _layer(contours=()):
    layer = fontforge.layer()
    layer.is_quadratic = True
    for c in contours:
        layer += c.dup()
    return layer


def _flag(layer):
    """Contours FontForge → [(x, y, sur_la_courbe)] pour lib.scanline."""
    return [[(p.x, p.y, p.on_curve) for p in c] for c in layer]


def _width(layer):
    x0, _, x1, _ = layer.boundingBox()
    return x1 - x0


def ring_scale(outer_width, inner_width, ring_width, target_stroke):
    """Échelle s et épaississement e pour qu'un anneau mesure ring_width de
    large et target_stroke d'épaisseur de paroi. Épaissir de e ajoute e à la
    largeur et e à la paroi : s·W + e = ring_width, s·paroi + e = target_stroke.
    e ≤ 0 → l'anneau réduit est déjà assez épais, pas d'épaississement."""
    stroke = (outer_width - inner_width) / 2
    s = (ring_width - target_stroke) / (outer_width - stroke)
    return s, ring_width - s * outer_width


def redesign_percents(font, stem, cell):
    for name, lay in LAYOUTS.items():
        glyph = font[name]
        orig = list(glyph.foreground)
        first_ring = lay["rings"][0][0]
        # plus la graisse est forte, plus on accepte une petite contreforme
        counter = max(30, lay["min_counter"] - COUNTER_PER_STEM * (stem - 112))
        target = min(RING_STROKE * stem, (lay["ring_width"] - counter) / 2)
        s, e = ring_scale(_width(_layer([orig[first_ring[0]]])),
                          _width(_layer([orig[first_ring[1]]])),
                          lay["ring_width"], target)
        rings = []
        for indices, anchor, left in lay["rings"]:
            ring = _layer(orig[i] for i in indices)
            _, y0, _, y1 = ring.boundingBox()
            ring.transform(psMat.scale(s, s))
            x0, ny0, _, ny1 = ring.boundingBox()
            dy = (y1 - ny1) if anchor == "top" else (y0 - ny0)
            ring.transform(psMat.translate(left - x0, dy))
            glyph.foreground = ring
            if e > 2:
                embolden(glyph, e)
            rings.append(glyph.foreground.dup())
        # barre épaissie, plus couchée tant qu'elle frôle un anneau : ses
        # extrémités s'écartent alors des anneaux (haut-gauche, bas-droite).
        # En gras, elle est plus épaisse que dans le Regular d'après lequel
        # LAYOUTS est réglé.
        shear = 0.0
        while True:
            bar = _layer([orig[lay["bar"]]])
            bar.transform(psMat.scale(lay["bar_scale"], 1))
            x0, y0, x1, y1 = bar.boundingBox()
            cy = (y0 + y1) / 2
            # cisaillement autour du centre : la barre se couche sans
            # s'épaissir horizontalement
            bar.transform(psMat.compose(psMat.translate(0, -cy), psMat.compose(
                psMat.skew(math.atan(shear)), psMat.translate(0, cy))))
            x0, _, x1, _ = bar.boundingBox()
            bar.transform(psMat.translate(lay["bar_center"] - (x0 + x1) / 2, 0))
            glyph.foreground = bar
            embolden(glyph, BAR_EMBOLDEN * stem)
            bar = glyph.foreground.dup()
            gap = min(min_distance(_flag(bar), _flag(r)) for r in rings)
            if gap >= CLEARANCE or shear + BAR_SHEAR_STEP > BAR_SHEAR_MAX:
                break
            shear += BAR_SHEAR_STEP
        print(f"{name} : cisaillement {shear:.2f}, blanc {gap}")
        layer = _layer()
        for part in rings + [bar]:
            for c in part:
                layer += c
        glyph.foreground = layer
        glyph.removeOverlap()
        x0, _, x1, _ = glyph.boundingBox()
        glyph.transform(psMat.translate((cell - (x1 - x0)) / 2 - x0, 0))
        glyph.correctDirection()
        glyph.round()
        glyph.width = cell
