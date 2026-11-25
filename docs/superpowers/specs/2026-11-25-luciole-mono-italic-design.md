# Luciole Mono Italic et Bold Italic — design court

**Intention.** Compléter la famille avec les italiques, pour le terminal et le code (commentaires, emphase).

**Constat.** Luciole Italic et Bold Italic sont des obliques : les mêmes dessins que le droit, penchés de 15°, avec les mêmes chasses. Passés tels quels dans `build.py`, ils cassent les redessins pensés pour des fûts verticaux (`i` en pavé, `l` cassé, `%` abîmé).

**Approches.**
1. *(choisie par l'utilisateur)* Pencher les fontes mono droites finies. Cela garde tous les réglages validés : `%`, `0` barré, `i` `l` `r`, `I` gras.
2. Redresser la source italique, la traiter, puis la repencher. On obtient le même dessin par un chemin plus long et plus fragile.

**Design.**
- `italicize.py` (fontTools) lit `dist/LucioleMono-{Regular,Bold}.ttf` et écrit `dist/LucioleMono-{Italic,BoldItalic}.ttf`.
- **Inclinaison.** x' = x + (y − Y0)·tan 15°. Y0 = 385 est mesuré sur Luciole : le `n` droit commence à 90, l'italique à −13. La chasse reste celle de la cellule (620), et les débords penchés sont normaux pour une italique.
- **Métadonnées.**
  - `post.italicAngle` = −15 ;
  - `hhea.caretSlopeRise/Run` et `caretOffset` réglés pour la pente ;
  - `OS/2.fsSelection` : bit ITALIC levé, bit REGULAR effacé, bit BOLD gardé ;
  - `head.macStyle` : bit italique levé.
- **Noms.**
  - Famille « Luciole Mono » ;
  - styles « Italic » et « Bold Italic » ;
  - noms PostScript `LucioleMono-Italic` et `LucioleMono-BoldItalic`.
- **Construction.** `make build` construit les italiques après les droits, et `make install` les copie. `make specimen` couvre aussi les italiques.

**Hors champ.** Vraies formes cursives (Luciole n'en a pas) ; italique propre à chaque glyphe.

**Mes choix.** La valeur Y0 = 385 vient de la mesure ci-dessus. Les tests ne vérifient que la transformation, pas la lisibilité ; celle-ci est vérifiée à l'œil sur les planches.
