"""Paramètres de construction de Luciole Mono (réglables)."""
import os

# Graisse construite : LUCIOLE_STYLE=Regular|Bold (le Makefile fait les deux)
# Italic et BoldItalic sont produits par italicize.py à partir des droits ;
# leur STYLE ne sert qu'aux planches (comparaison avec la source).
STYLE = os.environ.get("LUCIOLE_STYLE", "Regular")
SOURCE_FILE = {"BoldItalic": "Bold_Italic"}
# Polices Luciole d'origine (CC-BY 4.0), fournies dans le dépôt
LUCIOLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources", "luciole")
ORIGINAL = {s: f"{LUCIOLE_DIR}/Luciole_{SOURCE_FILE.get(s, s)}.ttf"
            for s in ("Regular", "Bold", "Italic", "BoldItalic")}
# Graisses dont la source est fabriquée par make_source.py : (graisse de
# Luciole d'origine, épaississement des traits). Le gras de Luciole Mono est
# un demi-gras : Luciole Bold (fûts 200) remplissait trop la cellule de 620
# (0 bouché, m M W tassés) ; Regular + 44 donne des fûts de 156.
DERIVED = {"Bold": ("Regular", 44)}
SOURCE = (os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", f"source-{STYLE}.ttf")
          if STYLE in DERIVED else ORIGINAL.get(STYLE))
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
STYLE_OVERRIDES = {"Bold": {"ZERO_INK": 0.83, "I_INK": 0.8}}
GAP_PERCENTILE = 0.75            # espace intérieur pris en compte (formes en coin : w, v)
VISIBLE_GAP = 17                 # espace blanc encore visible (unités)
SEPARATION = 25                  # blanc minimal entre deux morceaux d'encre (points, chevrons)
SIDE_ACCENT_AREA = 0.35          # accent latéral (ď, ŉ) : boîte < 35 % de celle de la lettre
SIDE_MIN_SCALE = 0.6             # réduction maximale d'un accent latéral
KEEP_GAPS = 0.6                  # part des espaces visibles gardés à l'épaississement
                                 # (tests : 0,5 ; sans cela le M gras se bouche)

# Italiques : nom PostScript → (droit d'origine, nom de style)
ITALICS = {"Italic": ("Regular", "Italic"), "BoldItalic": ("Bold", "Bold Italic")}
SLANT = 15                       # degrés, comme Luciole Italic
SLANT_Y0 = 385                   # hauteur fixe de l'inclinaison (n : 90 → −13 dans Luciole)

globals().update(STYLE_OVERRIDES.get(STYLE, {}))   # en dernier
