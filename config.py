"""Paramètres de construction de Luciole Mono (réglables)."""
import os

SOURCE = os.path.expanduser(
    "~/.local/share/fonts/typographies.fr/TrueType/Luciole/Luciole_Regular.ttf")
CELL = 620
NEAR_TOLERANCE = 0.10
MARGIN = 30                      # approche minimale des glyphes compressés
FAMILY = "Luciole Mono"
STYLE = "Regular"
PS_NAME = "LucioleMono-Regular"
ZERO_WIDTH = ("NULL", ".null")
NARROW_REDESIGN = ["i", "j", "l", "I", "one", "r", "f", "t", "dotlessi", "dotlessj"]
STAGE1 = "build/stage1.ttf"
