# Luciole Mono Italic — plan

**Spec :** docs/superpowers/specs/2026-11-25-luciole-mono-italic-design.md

### Task 1: italicize.py + tests + Makefile + README

- [ ] Écrire tests/test_italic.py. Paramétré sur (Italic, Regular, « Italic ») et (BoldItalic, Bold, « Bold Italic »), il vérifie :
  - chaque point = point droit incliné (x + (y − 385)·tan 15°, arrondi) ;
  - chasses et cmap identiques au droit ;
  - lsb = xMin ;
  - italicAngle = −15 ;
  - fsSelection (ITALIC levé, REGULAR effacé, BOLD gardé) et macStyle ;
  - les noms 1, 2, 4, 6, 16, 17 ;
  - isFixedPitch.
- [ ] Le lancer : il échoue (fichiers absents).
- [ ] Écrire italicize.py. Mettre dans config `UPRIGHT_OF` et le nom de fichier source de Bold Italic.
- [ ] Ajouter au Makefile `ITALICS` (build, specimen).
- [ ] Faire passer les tests, puis lancer `make all`.
- [ ] Planches, README, commit.
