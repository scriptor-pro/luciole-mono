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
EMBOLDEN = 0.6                   # part de l'amincissement compensée (1 = traits verticaux)
