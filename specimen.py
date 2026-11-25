"""Planches de contrôle visuel : make specimen → specimens/*.png"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

import config  # noqa: E402
from render import render  # noqa: E402

DIST = str(ROOT / "dist" / f"{config.PS_NAME}.ttf")

ALPHABET = ("abcdefghijklmnopqrstuvwxyz\nABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
            "0123456789 %&@#$€‰ ½™ ⇒ ←→\n"
            "íìîïĩīĭįĵĺļľŀłŕŗřţťŧÍÌÎÏ")
CONFUSABLES = "Il1| O0o '`ʼ\" ;:.,"
CODE = '''def moyenne(valeurs: list[float]) -> float:
    if not valeurs:  # liste vide → 0
        return 0.0
    return sum(valeurs) / len(valeurs)  # {i}[l]1|0O

for f in *.ttf; do fc-query -f '%{family}\\n' "$f"; done
grep -rnE "^(l|1|I)\\s*=" src/ && echo "ok" || exit 1'''


def stack(images, pad=20, labels=None):
    w = max(i.width for i in images) + 2 * pad
    h = sum(i.height for i in images) + pad * (len(images) + 1)
    out = Image.new("L", (w, h), 255)
    y = pad
    draw = ImageDraw.Draw(out)
    for idx, im in enumerate(images):
        out.paste(im, (pad, y))
        if labels:
            draw.text((pad, y), labels[idx], fill=128)
        y += im.height + pad
    return out


def column_grid(img, font_path, px):
    """Filigrane : une ligne verticale grise par colonne de caractère."""
    cell = ImageFont.truetype(font_path, px).getlength("n")
    rgb = img.convert("RGB")
    draw = ImageDraw.Draw(rgb)
    x = px
    while x < img.width:
        draw.line([(x, 0), (x, img.height)], fill=(225, 235, 250))
        x += cell
    # repasser le texte par-dessus la grille
    return Image.composite(img.convert("RGB"), rgb,
                           img.point(lambda p: 255 if p < 200 else 0))


def atkinson_mono():
    out = subprocess.run(["fc-match", "-f", "%{file}", "Atkinson Hyperlegible Mono"],
                         capture_output=True, text=True).stdout.strip()
    return out


def main(out_dir: Path = ROOT / "specimens"):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stack([render(config.SOURCE, ALPHABET, 48), render(DIST, ALPHABET, 48)],
          labels=["Luciole (source)", "Luciole Mono"]).save(out_dir / "alphabet.png")
    stack([render(DIST, CONFUSABLES, px) for px in (12, 18, 48)]
          ).save(out_dir / "confusables.png")
    stack([column_grid(render(DIST, CODE, px), DIST, px).convert("L")
           for px in (12, 14, 18)]).save(out_dir / "code.png")
    stack([render(DIST, CODE, 16), render(atkinson_mono(), CODE, 16)],
          labels=["Luciole Mono", "Atkinson Hyperlegible Mono"]
          ).save(out_dir / "vs-atkinson.png")


if __name__ == "__main__":
    main()
