# Luciole Mono

Version à chasse fixe de la police **Luciole**, pour le terminal et l'éditeur de code.

Luciole a été conçue pour les personnes malvoyantes par Laurent Bourcellier et Jonathan Perez (Centre Technique Régional pour la Déficience Visuelle, typographies.fr). Luciole Mono reprend son dessin et l'adapte à une grille où tous les caractères ont la même largeur.

## Licence et attribution

Luciole © Laurent Bourcellier & Jonathan Perez, distribuée sous licence [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/legalcode.fr).

Luciole Mono (Regular, Bold, Italic et Bold Italic) est une **œuvre dérivée** de Luciole (Regular, Bold, Italic, Bold Italic), distribuée sous la même licence CC-BY 4.0. Modifications apportées :

- tous les glyphes ont une largeur de 620 unités (1000 unités/em) ;
- les glyphes larges (`m`, `w`, `M`, `W`, `@`…) sont compressés, puis épaissis horizontalement pour retrouver l'épaisseur de leurs traits, sans jamais refermer leurs espaces intérieurs. Dans le Regular, les fûts de `m` sont conservés tels quels (`condenseExtend`) ;
- `i`, `j`, `l` et `r` sont redessinés avec des empattements (et une queue courbe pour `l`) pour occuper la cellule et éviter les confusions ;
- les lettres accentuées sur ces bases sont reconstruites ;
- `%` et `‰` sont redessinés : leurs anneaux sont réduits mais restent ronds, placés de part et d'autre de la barre oblique ;
- le zéro barré de Luciole (`zero.slash`) devient le `0` par défaut, plus étroit que `O` ;
- en gras, `I` est resserré pour se distinguer du `1` ;
- Italic et Bold Italic sont les versions droites penchées de 15°, comme Luciole Italic (une oblique du droit) : elles gardent tous les redessins ci-dessus ;
- le crénage (`kern`), les ligatures (`liga`) et le hinting TrueType ont été retirés, et les métadonnées sont celles d'une police monospace.

## Construire

Dépendances : FontForge (≥ 20230101), Python 3, et `fonttools`, `pillow`, `pytest` dans `.venv` :

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
make all         # pour chaque graisse : FontForge → dist/LucioleMono-<graisse>.ttf,
                 # puis italicize.py (Italic, BoldItalic), puis les tests
make specimen    # planches de contrôle dans specimens/
make install     # copie dans ~/.local/share/fonts/LucioleMono/ et fc-cache
```

Les réglages (largeur de cellule, marge, épaississement, réglages propres au gras) se trouvent dans `config.py`. Les dimensions (fût, barre du `t`, hauteurs) sont mesurées sur chaque police source (`lib/geometry.py`). Les formes redessinées sont dans `lib/narrow.py` et `lib/symbols.py`. L'inclinaison (`SLANT`, `SLANT_Y0`) est dans `config.py`, appliquée par `italicize.py`. Pour construire une seule graisse : `make all STYLES=Bold` (les italiques sont refaits à partir des droits présents dans `dist/`).

## Limites connues

- En gras, la cellule (620) est étroite pour Luciole Bold (son `n` fait 686) : `m`, `M`, `W` et les symboles larges ont des traits plus fins que les autres lettres grasses.
- `⇔` est peu lisible dans les deux graisses.
- Les italiques débordent un peu de la cellule en haut à droite et en bas à gauche, comme toute italique monospace.
- `ł`, `į`, `ⁱ` et `ℓ` gardent le dessin d'origine, centré : leur accent est soudé à la lettre dans Luciole.

## Prochaines étapes

Aucune prévue ; voir les limites ci-dessus.
