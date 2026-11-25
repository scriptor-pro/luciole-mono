"""Paramètres de construction de Luciole Mono (réglables)."""
import os

# Graisse construite : LUCIOLE_STYLE=Regular|Bold (le Makefile fait les deux)
STYLE = os.environ.get("LUCIOLE_STYLE", "Regular")
SOURCE = os.path.expanduser(
    f"~/.local/share/fonts/typographies.fr/TrueType/Luciole/Luciole_{STYLE}.ttf")
CELL = 620
NEAR_TOLERANCE = 0.10
MARGIN = 30                      # approche minimale des glyphes compressés
FAMILY = "Luciole Mono"
PS_NAME = f"LucioleMono-{STYLE}"
ZERO_WIDTH = ("NULL", ".null")
# Redessinés en coordonnées de cellule par lib/narrow.py (pas de recentrage).
# I, 1, f, t : le dessin de Luciole les distingue déjà, gardés tels quels.
NARROW_REDESIGN = ["i", "j", "l", "r", "dotlessi", "dotlessj"]
STAGE1 = f"build/stage1-{STYLE}.ttf"
CONDENSE_EXTEND = ["m"]          # glyphes à fûts verticaux purs
EMBOLDEN = 1.0                   # part de l'amincissement horizontal compensée
MIN_GAP = 0.2                    # espace intérieur minimal après épaississement (× fût)
MIN_CONDENSE = 0.3               # en dessous, condenseExtend écrase les contreformes
ZERO_INK = 0.86                  # largeur d'encre des zéros (× place), plus étroits que O
I_INK = 1.0                      # largeur d'encre de I (× place)

# Réglages propres à une graisse : en gras, I et 0 remplissent la cellule
# comme 1 et O ; on les resserre pour garder les différences de silhouette.
STYLE_OVERRIDES = {"Bold": {"ZERO_INK": 0.80, "I_INK": 0.65}}
GAP_PERCENTILE = 0.75            # espace intérieur pris en compte (formes en coin : w, v)

globals().update(STYLE_OVERRIDES.get(STYLE, {}))   # en dernier
