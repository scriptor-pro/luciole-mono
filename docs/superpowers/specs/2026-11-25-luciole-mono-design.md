# Luciole Mono — design

*2026-11-25*

## Intention

Créer une version à chasse fixe de la police Luciole pour le terminal et l'éditeur de code. Luciole a été conçue pour les personnes malvoyantes. Atkinson Hyperlegible a une version mono, Luciole non.

## Objectifs

- Tous les caractères de Luciole Regular (682 caractères codés) ont la même largeur.
- Les paires que l'on confond en programmation se distinguent au premier coup d'œil : `l` `1` `I` `|`, `0` `O` `o`, `` ` `` `'`, `;` `:`, `.` `,`.
- Les lettres gardent la graisse et l'esprit de Luciole. Une lettre compressée ne doit pas paraître plus maigre que ses voisines.
- Fontconfig reconnaît la police comme monospace (`spacing=100`), et un terminal peut la sélectionner.

## Hors objectifs (pour l'instant)

- Ligatures de programmation (`=>`, `!=`…), glyphes Nerd Font/Powerline, police variable.
- Gras et italique : ils viennent **après** validation du regular, avec le même script.

## Ce qui ferait échouer le projet, même si la police « marche »

- Des lettres visiblement déformées (`m` ou `W` écrasés et maigres).
- Des `i` et des `l` perdus au milieu d'un grand blanc, qui hachent la lecture.
- Un `l` et un `1` (ou un `0` et un `O`) encore confondables.

## Approches envisagées

| Approche | Résumé | Verdict |
|---|---|---|
| A. Conversion automatique (fontTools) | Largeur unique, compression et centrage | Écartée : les confusions de caractères restent et la graisse devient inégale |
| **B. Conversion automatique et redessin par script (FontForge)** | Compression qui préserve les fûts, empattements ajoutés aux lettres étroites, zéro marqué | **Retenue** |
| C. Redessin entièrement manuel | Le meilleur résultat, mais des dizaines d'heures | Écartée : trop coûteuse |
| Emprunter des glyphes à Atkinson Mono | — | Écartée : styles incompatibles, et les licences OFL et CC-BY se combinent mal |

## Source et licence

- Source : `~/.local/share/fonts/typographies.fr/TrueType/Luciole/Luciole_Regular.ttf` (v1.001, 1000 unités/em, 755 glyphes, hauteur d'x 545, hauteur de capitale 763).
- Licence CC-BY 4.0 : les dérivés sont autorisés avec attribution. Nom distinct : **Luciole Mono**. Le copyright d'origine (« Luciole © Laurent Bourcellier & Jonathan Perez ») est conservé dans les métadonnées et le README, avec la mention des modifications.

## Fonctionnement

Outil : un script Python exécuté par `fontforge -script` (FontForge 20230101 est installé, son module Python n'est disponible que par ce moyen). Le script est relançable de bout en bout, et toutes les valeurs réglables se trouvent en tête de fichier.

1. **Largeur de cellule : 620 unités** *(mon choix)*. C'est la largeur du `n` de Luciole : la plupart des minuscules (`n` 620, `o` 593) ne bougent presque pas. Le `m` (930) est réduit à environ 67 %. Cette valeur se règle d'un paramètre si on veut un texte plus serré.
2. **Classement des glyphes** selon leur largeur d'origine :
   - *proches de la cellule* (environ ±10 %) : simplement recentrés ;
   - *larges* (`m w M W @ % & —`…) : compressés avec `condenseExtend` de FontForge, qui rétrécit les contreformes tout en conservant l'épaisseur des fûts. Un épaississement léger est ajouté si nécessaire ;
   - *étroits* (`i l j r f t 1 I` et leurs accentués) : redessinés (étape 3) ;
   - *ponctuation étroite* (`. , : ; ' " ! |`…) : centrée, sans modification.
3. **Redessin des lettres étroites**, avec des empattements construits à partir de l'épaisseur des fûts de Luciole :
   - `i` et `j` : empattement d'attaque à gauche, `i` avec un pied horizontal ;
   - `l` : empattement d'attaque, terminé par une queue courbe vers la droite (la forme la plus différente de `1` et de `I`) ;
   - `I` : empattements en haut et en bas ;
   - `1` : drapeau plus prononcé et socle ;
   - `r`, `f`, `t` : traits horizontaux allongés pour remplir la cellule ;
   - `|` : reste une barre simple et pleine hauteur, donc différente de `l` et de `I`.
4. **Zéro** : le zéro barré déjà dessiné par les auteurs de Luciole (`zero.slash`, feature `zero`) devient le `0` par défaut. *(Changement décidé pendant la rédaction du plan : il remplace le point prévu au départ, car il est fidèle au dessin d'origine.)*
5. **Composites et accents** : les lettres accentuées doivent suivre leur base (`í î ï` suivent le nouveau `i`). On vérifie que les accents restent centrés au-dessus du glyphe.
6. **Nettoyage spécifique au mono** : suppression du crénage (GPOS `kern`) et des ligatures qui modifient la largeur (`ﬁ`, `ﬂ` décomposées ou retirées). Les glyphes de largeur nulle (diacritiques combinants) restent à largeur nulle.
7. **Métadonnées** : nom de famille « Luciole Mono », `post.isFixedPitch = 1`, OS/2 PANOSE proportion = 9 (monospace), `xAvgCharWidth` = 620, mention des modifications dans la licence et la description.
8. **Hinting** : les instructions TrueType d'origine ne correspondent plus aux contours modifiés. On les retire, et on passe ttfautohint s'il est disponible. Sinon, la police reste sans hinting, ce qui passe bien avec le lissage de Linux.

## Vérification

- Script de contrôle (fontTools) : chaque glyphe codé a une largeur de 0 ou de 620, et les métadonnées mono sont présentes.
- `fc-query` / `fc-list :spacing=mono` : la police est bien reconnue comme monospace.
- **Planches PNG** générées à chaque build :
  - comparaison avant/après de l'alphabet ;
  - ligne des confusions : `Il1| O0o 'ʼ\` ;:.,` ;
  - extrait de code (Python, shell) en 12, 14 et 18 px ;
  - comparaison avec Atkinson Hyperlegible Mono à la même taille.
- Validation finale par l'utilisateur dans son terminal et son éditeur.

## Livrables (dans `~/Documents/Projets/luciole-mono/`)

- `build.py` : script FontForge de génération ;
- `check.py` : vérifications fontTools ;
- `specimen.py` : planches PNG ;
- `dist/LucioleMono-Regular.ttf` ;
- `README.md` : attribution CC-BY, mode de reconstruction, liste des modifications.

## Laissé au constructeur

Les valeurs exactes des empattements, le seuil de « proche de la cellule », le facteur d'épaississement et le choix de condenser ou de redessiner chaque glyphe large particulier : tout se règle au vu des planches, en itérant.
