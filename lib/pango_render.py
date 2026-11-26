"""Rendu de texte par Pango (pango-view), comme dans les applications du
bureau : hinting « slight », lissage en niveaux de gris.

Pillow applique un hinting complet ; sur une police sans instructions,
FreeType le remplace par l'autohinter, qui cale chaque glyphe à part sur la
grille de pixels (Ü ne tombait pas sur les mêmes pixels que U). Les planches
montraient donc des gris que l'utilisateur ne voit pas."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image


def _family_style(font_file):
    name = TTFont(font_file, lazy=True)["name"]
    family = name.getDebugName(16) or name.getDebugName(1)
    style = name.getDebugName(17) or name.getDebugName(2)
    return family, style


def render_pango(font_file, text, px, hinting="slight"):
    """Texte noir sur fond blanc (image « L »), rendu par pango-view avec ce
    seul fichier de police visible de fontconfig."""
    family, style = _family_style(font_file)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "fonts").mkdir()
        shutil.copy(font_file, tmp / "fonts")
        (tmp / "fonts.conf").write_text(
            f'<?xml version="1.0"?>\n<fontconfig><dir>{tmp / "fonts"}</dir>'
            f'<cachedir>{tmp / "cache"}</cachedir></fontconfig>\n')
        (tmp / "text.txt").write_text(text)
        weight_slant = "" if style == "Regular" else f" {style}"
        subprocess.run(
            ["pango-view", "-q", f"--font={family}{weight_slant} {px}px",
             f"--hinting={hinting}", "--antialias=gray", f"--margin={px}",
             "-o", str(tmp / "out.png"), str(tmp / "text.txt")],
            check=True, env={**os.environ, "FONTCONFIG_FILE": str(tmp / "fonts.conf")},
            capture_output=True)
        with Image.open(tmp / "out.png") as im:
            out = Image.new("L", im.size, 255)
            rgba = im.convert("RGBA")
            out.paste(rgba.convert("L"), mask=rgba.getchannel("A"))
            return out
