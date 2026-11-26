"""Étape 0 (FontForge) : fabrique la source des graisses de config.DERIVED.

Le gras de Luciole Mono est un demi-gras : Luciole Regular dont chaque trait
est épaissi de DELTA (fûts 112 → 156). Chaque morceau d'encre (la lettre,
chaque accent) est épaissi à part puis ramené à sa propre hauteur : l'écart
entre accent et lettre reste celui de Luciole, et la lettre de í reste
identique à ı (l'accent peut alors être reconstruit sur le i redessiné).
Les chasses s'élargissent de DELTA ; build.py les ramène ensuite à la
cellule comme pour les autres graisses.

Usage : LUCIOLE_STYLE=Bold fontforge -script make_source.py (sans effet
pour une graisse qui n'est pas dans config.DERIVED)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fontforge  # noqa: E402
import psMat  # noqa: E402

import config  # noqa: E402
from lib.scanline import ink_groups  # noqa: E402
from lib.symbols import REDESIGNED  # noqa: E402


def _layer(contours, quadratic):
    layer = fontforge.layer()
    layer.is_quadratic = quadratic
    for c in contours:
        layer += c
    return layer


def thicken(glyph, delta):
    """Épaissit chaque morceau d'encre de delta (delta/2 de chaque côté),
    garde la hauteur de chacun, décale de delta/2 et élargit la chasse de
    delta (approches inchangées)."""
    if glyph.foreground.isEmpty():
        return
    quadratic = glyph.foreground.is_quadratic
    contours = list(glyph.foreground)
    flagged = [[(p.x, p.y, p.on_curve) for p in c] for c in contours]
    width = glyph.width
    out = _layer([], quadratic)
    for group in ink_groups(flagged):
        part = _layer([contours[i].dup() for i in group], quadratic)
        _, y0, _, y1 = part.boundingBox()
        glyph.foreground = part
        glyph.stroke("circular", delta, "butt", "miter")
        for c in part:
            glyph.foreground += c
        glyph.removeOverlap()
        _, ny0, _, ny1 = glyph.boundingBox()
        sy = (y1 - y0) / (ny1 - ny0)
        glyph.transform(psMat.compose(psMat.translate(delta / 2, -ny0),
                                      psMat.compose(psMat.scale(1, sy), psMat.translate(0, y0))))
        for c in glyph.foreground:
            out += c
    glyph.foreground = out
    glyph.removeOverlap()
    glyph.correctDirection()
    glyph.round()
    glyph.width = width + delta


def main():
    if config.STYLE not in config.DERIVED:
        return
    base, delta = config.DERIVED[config.STYLE]
    font = fontforge.open(config.ORIGINAL[base])
    for glyph in font.glyphs():
        # % et ‰ : redessinés par lib/symbols.py d'après l'ordre de leurs
        # contours (que l'épaississement changerait) et le fût mesuré
        if glyph.glyphname not in config.ZERO_WIDTH + REDESIGNED:
            thicken(glyph, delta)
    os.makedirs(os.path.dirname(config.SOURCE), exist_ok=True)
    font.generate(config.SOURCE, flags=("opentype",))
    font.close()


main()
