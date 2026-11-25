# Luciole Mono

Version à chasse fixe de la police **Luciole**, pour le terminal et l'éditeur de code.

Luciole a été conçue pour les personnes malvoyantes par Laurent Bourcellier et Jonathan Perez (Centre Technique Régional pour la Déficience Visuelle, typographies.fr). Luciole Mono reprend son dessin et l'adapte à une grille où tous les caractères ont la même largeur.

## Licence et attribution

Luciole © Laurent Bourcellier & Jonathan Perez, distribuée sous licence [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/legalcode.fr).

Luciole Mono (Regular et Bold) est une **œuvre dérivée** de Luciole Regular et Luciole Bold, distribuée sous la même licence CC-BY 4.0. Modifications apportées :

- tous les glyphes ont une largeur de 620 unités (1000 unités/em) ;
- les glyphes larges (`m`, `w`, `M`, `W`, `@`…) sont compressés, puis épaissis horizontalement pour retrouver l'épaisseur de leurs traits, sans jamais refermer leurs espaces intérieurs. Dans le Regular, les fûts de `m` sont conservés tels quels (`condenseExtend`) ;
- `i`, `j`, `l` et `r` sont redessinés avec des empattements (et une queue courbe pour `l`) pour occuper la cellule et éviter les confusions ;
- les lettres accentuées sur ces bases sont reconstruites ;
- `%` et `‰` sont redessinés : leurs anneaux sont réduits mais restent ronds, placés de part et d'autre de la barre oblique ;
- le zéro barré de Luciole (`zero.slash`) devient le `0` par défaut, plus étroit que `O` ;
- en gras, `I` est resserré pour se distinguer du `1` ;
- le crénage (`kern`), les ligatures (`liga`) et le hinting TrueType ont été retirés, et les métadonnées sont celles d'une police monospace.

## Construire

Dépendances : FontForge (≥ 20230101), Python 3, et `fonttools`, `pillow`, `pytest` dans `.venv` :

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
make all         # pour chaque graisse : FontForge → dist/LucioleMono-<graisse>.ttf, puis les tests
make specimen    # planches de contrôle dans specimens/
make install     # copie dans ~/.local/share/fonts/LucioleMono/ et fc-cache
```

Les réglages (largeur de cellule, marge, épaississement, réglages propres au gras) se trouvent dans `config.py`. Les dimensions (fût, barre du `t`, hauteurs) sont mesurées sur chaque police source (`lib/geometry.py`). Les formes redessinées sont dans `lib/narrow.py` et `lib/symbols.py`. Pour construire une seule graisse : `make all STYLES=Bold`.

## Limites connues

- En gras, la cellule (620) est étroite pour Luciole Bold (son `n` fait 686) : `m`, `M`, `W` et les symboles larges ont des traits plus fins que les autres lettres grasses.
- `⇔` est peu lisible dans les deux graisses.

- `ł`, `į`, `ⁱ` et `ℓ` gardent le dessin d'origine, centré : leur accent est soudé à la lettre dans Luciole.

## Prochaines étapes

Italique et gras italique, avec le même script (ajouter la graisse à `STYLES` dans le `Makefile`).
