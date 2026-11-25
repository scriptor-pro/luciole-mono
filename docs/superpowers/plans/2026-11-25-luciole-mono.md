# Luciole Mono — plan de réalisation

> **Pour les agents qui exécutent ce plan :** SOUS-SKILL REQUIS : superpowers:subagent-driven-development (recommandé) ou superpowers:executing-plans, pour réaliser le plan tâche par tâche. Les étapes utilisent des cases à cocher (`- [ ]`).

**Objectif :** produire `dist/LucioleMono-Regular.ttf`, une version monospace de Luciole Regular lisible pour le code.

**Architecture :** la construction se fait en deux étapes, enchaînées par un `Makefile`.
1. Un script FontForge (`build.py`, lancé par `fontforge -script`) modifie les contours et les largeurs, puis écrit `build/stage1.ttf`.
2. Un script fontTools (`finalize.py`) règle les métadonnées, les tables GSUB/GPOS et le hinting, puis écrit `dist/`.

La logique pure (classement des glyphes, appariement des contours pour les accents) se trouve dans `lib/`. Elle n'utilise que la bibliothèque standard et fontTools, qu'on peut importer depuis FontForge comme depuis le venv. Les tests pytest s'exécutent sur la police produite et sur les fonctions de `lib/`.

**Outils :** FontForge 20230101 (son module Python n'est disponible que via `fontforge -script`), fontTools, Pillow (rendu des glyphes dans les tests et les planches), pytest. pytest n'est pas installé sur le système : on crée un venv dans `luciole-mono/.venv`.

**Conception :** `docs/superpowers/specs/2026-11-25-luciole-mono-design.md`

## Contraintes globales

- Source : `~/.local/share/fonts/typographies.fr/TrueType/Luciole/Luciole_Regular.ttf` (1000 unités/em, hauteur d'x 545, hauteur de capitale 763). Elle n'est jamais modifiée.
- Largeur de cellule `CELL = 620`. **Tous** les glyphes de la police (y compris les variantes sans code Unicode, comme `zero.slash` ou `one.LT`) ont une largeur de 620. Les seules exceptions sont `NULL` et `.null`, qui ont une largeur de 0 (leur largeur d'origine, 65516, est invalide).
- Nom de famille « Luciole Mono », style « Regular », nom PostScript `LucioleMono-Regular`.
- Licence CC-BY 4.0 conservée. La notice contient « Luciole © Laurent Bourcellier & Jonathan Perez » et la mention « Modified: monospaced version (Luciole Mono) ».
- `post.isFixedPitch = 1`, `OS/2.panose.bProportion = 9`, `OS/2.xAvgCharWidth = 620`.
- Pas de feature GPOS `kern`, pas de `liga` (ligatures `f`).
- Aucun contour ne dépasse la cellule : `xMin >= 0` et `xMax <= 620`.
- Le projet a son propre dépôt git (`git init` dans `~/Documents/Projets/luciole-mono`, branche `main`). Les commits portent la ligne `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Points d'attention pour la relecture

1. **Glyphes sans code Unicode** atteints par des features OpenType (`smcp`, `onum`, `zero`, `tnum`…). Si un éditeur active ces features, une variante restée proportionnelle casse l'alignement. Le test `test_every_glyph_is_cell_width` porte donc sur l'ordre complet des glyphes (tâche 1), pas seulement sur la table `cmap`.
2. **Symboles très larges** (`‰` 1721, `⇔` 1439, `%` 1240, `½`, `™`) réduits à moins de 50 %. On attend qu'ils restent reconnaissables et qu'ils ne débordent pas de la cellule. Les tests `test_ink_inside_cell` (tâche 1) et `test_wide_glyph_stems_keep_weight` (tâche 3) s'en chargent, en plus d'un contrôle visuel sur la planche.
3. **Lettres accentuées dessinées d'un seul tenant** : Luciole ne contient aucun glyphe composite. Si on redessine `i`, les glyphes `í î ï ĩ ī ĭ į ì` ne suivent pas tout seuls. Le test `test_accented_follow_redesigned_base` (tâche 5) vérifie qu'ils le font.
4. **Espaces** (U+0020, U+00A0, espaces fines) : elles doivent aussi faire 620, sinon les colonnes se décalent. C'est couvert par le test `test_every_glyph_is_cell_width`.
5. **Rendu en petite taille** (12 px dans un terminal) : les empattements ajoutés ne doivent pas faire une tache. On le vérifie sur la planche à 12 px (tâche 2), puis l'utilisateur valide en vrai (tâche 6).

---

### Task 1: squelette, construction minimale et tests de conformité mono

**Fichiers :**
- Créer : `luciole-mono/Makefile`, `luciole-mono/requirements.txt`, `luciole-mono/.gitignore`, `luciole-mono/config.py`, `luciole-mono/build.py`, `luciole-mono/finalize.py`, `luciole-mono/lib/__init__.py`, `luciole-mono/lib/classify.py`
- Tests : `luciole-mono/tests/conftest.py`, `luciole-mono/tests/test_conformity.py`, `luciole-mono/tests/test_classify.py`

**Interfaces :**
- Produit :
  - `config.py` : `SOURCE: str`, `CELL = 620`, `NEAR_TOLERANCE = 0.10`, `FAMILY = "Luciole Mono"`, `PS_NAME = "LucioleMono-Regular"`, `NARROW_REDESIGN = ["i","j","l","I","one","r","f","t","dotlessi","uni0237"]` (à compléter avec les noms réels trouvés dans la police) ;
  - `lib/classify.py` : `classify(width: int, cell: int, tol: float) -> Literal["near","wide","narrow"]` ;
  - `tests/conftest.py` : fixture `font` (TTFont de `dist/LucioleMono-Regular.ttf`) et fixture `source` (TTFont de la source) ;
  - commandes `make build`, `make test`, `make all`.

- [ ] **Étape 1 :** créer `requirements.txt` (`fonttools`, `pillow`, `pytest`), le `.gitignore` (`.venv/`, `build/`, `__pycache__/`), puis lancer `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Résultat attendu : `.venv/bin/pytest --version` affiche une version.
- [ ] **Étape 2 : écrire les tests qui échouent**

```python
# tests/test_classify.py
def test_classify():
    assert classify(620, 620, .10) == "near"
    assert classify(593, 620, .10) == "near"
    assert classify(930, 620, .10) == "wide"
    assert classify(292, 620, .10) == "narrow"
    assert classify(682, 620, .10) == "near"   # limite incluse
    assert classify(683, 620, .10) == "wide"

# tests/test_conformity.py
def test_every_glyph_is_cell_width(font):
    for name in font.getGlyphOrder():
        expected = 0 if name in ("NULL", ".null") else 620
        assert font["hmtx"][name][0] == expected, name
def test_same_codepoints_as_source(font, source):
    assert set(font.getBestCmap()) == set(source.getBestCmap())
def test_fixed_pitch_metadata(font):
    assert font["post"].isFixedPitch == 1
    assert font["OS/2"].panose.bProportion == 9
    assert font["OS/2"].xAvgCharWidth == 620
def test_names(font):
    n = font["name"]
    assert n.getDebugName(1) == "Luciole Mono" and n.getDebugName(6) == "LucioleMono-Regular"
    assert "Bourcellier" in n.getDebugName(13) and "Luciole Mono" in n.getDebugName(13)
def test_no_kern_no_liga(font):
    tags = lambda t: {r.FeatureTag for r in font[t].table.FeatureList.FeatureRecord}
    assert "kern" not in tags("GPOS") if "GPOS" in font else True
    assert "liga" not in tags("GSUB")
def test_ink_inside_cell(font):
    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.numberOfContours:
            assert g.xMin >= 0 and g.xMax <= 620, name
def test_fontconfig_sees_mono():
    out = subprocess.run(["fc-query", "-f", "%{spacing}", DIST], capture_output=True, text=True).stdout
    assert out.strip() == "100"
```

- [ ] **Étape 3 :** lancer `make test`. Résultat attendu : ÉCHEC (la police `dist/` n'existe pas, `classify` non plus).
- [ ] **Étape 4 :** écrire `classify` dans `lib/classify.py`. Le résultat est `near` quand `|w − cell| ≤ tol × cell`.
- [ ] **Étape 5 :** écrire la version minimale de `build.py`. Le script ouvre `SOURCE`. Pour chaque glyphe : s'il est `wide`, il le réduit horizontalement par une simple mise à l'échelle (ce sera amélioré à la tâche 3) jusqu'à `CELL − 2 × 30` d'encre ; dans tous les cas, il le centre (même approche à gauche et à droite) et fixe sa largeur à `CELL`. `NULL` et `.null` passent à 0. Le script écrit `build/stage1.ttf` avec `generate(..., flags=("opentype",))`.
- [ ] **Étape 6 :** écrire `finalize.py`. Il lit `stage1.ttf` puis : renomme (IDs 1, 2, 3, 4, 6, 16, 17), ajoute la mention de modification à l'ID 13, règle `isFixedPitch`, `bProportion = 9` et `xAvgCharWidth`, retire la feature `kern` de GPOS et `liga` de GSUB (enlever les FeatureRecords concernés de la FeatureList et des LangSys), retire `fpgm`, `prep`, `cvt ` et les instructions des glyphes (fontTools : `glyph.program = ttProgram.Program(); glyph.program.fromBytecode(b"")`), puis écrit `dist/LucioleMono-Regular.ttf`.
- [ ] **Étape 7 :** écrire le `Makefile`. `build` lance `fontforge -script build.py && .venv/bin/python finalize.py`, `test` lance `.venv/bin/pytest -q`, et `all` enchaîne `build test`.
- [ ] **Étape 8 :** lancer `make all`. Résultat attendu : tous les tests passent.
- [ ] **Étape 9 : commit** `feat(luciole-mono): construction mono minimale et tests de conformité`

### Task 2: planches de contrôle visuel

**Fichiers :**
- Créer : `luciole-mono/specimen.py`, `luciole-mono/tests/render.py`
- Test : `luciole-mono/tests/test_specimen.py`

**Interfaces :**
- Produit :
  - `tests/render.py` : `render(font_path: str, text: str, px: int) -> PIL.Image.Image` (en niveaux de gris, encre noire sur fond blanc) ;
  - `tests/render.py` : `ink_runs(font_path: str, char: str, y_units: int) -> list[int]` : longueurs, en unités de la police, des segments d'encre sur la ligne horizontale `y_units` au-dessus de la ligne de base. Le glyphe est rendu à 1000 px, donc 1 px = 1 unité ;
  - `make specimen`, qui écrit `specimens/*.png`.

- [ ] **Étape 1 : écrire le test qui échoue**

```python
def test_specimens_written(tmp_path):
    specimen.main(out_dir=tmp_path)
    for name in ("alphabet.png", "confusables.png", "code.png", "vs-atkinson.png"):
        assert (tmp_path / name).stat().st_size > 0
def test_ink_runs_n_has_two_stems():
    assert len(ink_runs(DIST, "n", 270)) == 2
```

- [ ] **Étape 2 :** lancer `.venv/bin/pytest tests/test_specimen.py`. Résultat attendu : ÉCHEC (module introuvable).
- [ ] **Étape 3 :** écrire `render`, `ink_runs` et `specimen.main(out_dir: Path)`. Contenu des planches :
  - `alphabet.png` : la source et la version mono, l'une au-dessus de l'autre, en 48 px ;
  - `confusables.png` : `Il1| O0o 'ʼ\` ;:.,` en 12, 18 et 48 px ;
  - `code.png` : un extrait Python et un extrait shell en 12, 14 et 18 px, avec une grille de colonnes en filigrane ;
  - `vs-atkinson.png` : le même code dans Atkinson Hyperlegible Mono, trouvé avec `fc-match -f '%{file}' 'Atkinson Hyperlegible Mono'`.
- [ ] **Étape 4 :** lancer `make all specimen`. Résultat attendu : les tests passent et les quatre PNG existent. **Montrer `alphabet.png` et `confusables.png` à l'utilisateur** : c'est le point de référence avant les améliorations.
- [ ] **Étape 5 : commit** `feat(luciole-mono): planches de contrôle`

### Task 3: compression des glyphes larges en conservant la graisse

**Fichiers :**
- Modifier : `luciole-mono/build.py` (traitement des glyphes `wide`)
- Test : `luciole-mono/tests/test_weight.py`

**Interfaces :**
- Utilise : `ink_runs` (tâche 2), `classify` (tâche 1).

- [ ] **Étape 1 : écrire le test qui échoue**

```python
STEM_N = statistics.mean(ink_runs(DIST, "n", 270))
@pytest.mark.parametrize("ch,y", [("m",270),("w",270),("M",380),("W",380),("H",380)])
def test_wide_glyph_stems_keep_weight(ch, y):
    stems = ink_runs(DIST, ch, y)
    assert stems and min(stems) >= 0.9 * STEM_N * (1.07 if ch.isupper() else 1)
```

Le coefficient 1,07 tient compte du fait que les capitales de Luciole ont des fûts un peu plus épais. On le mesure d'abord sur la source avec `ink_runs(SOURCE, "H", 380)` et on corrige la valeur si elle diffère.

- [ ] **Étape 2 :** lancer le test. Résultat attendu : ÉCHEC sur `m`, `M` et `W`, car la simple mise à l'échelle les a amincis.
- [ ] **Étape 3 :** dans `build.py`, remplacer la mise à l'échelle par `glyph.condenseExtend(factor, 0)`, avec `factor = (CELL − 60) / largeur_encre`. Si les fûts restent trop fins, ajouter un `glyph.changeWeight(delta, "LCG", 0, 0, "auto")`, où `delta` est la différence entre le fût de `n` et le fût mesuré. Corriger ensuite les contours (`removeOverlap()`, `correctDirection()`, `round()`), puis recentrer.
- [ ] **Étape 4 :** lancer `make all specimen`. Résultat attendu : tous les tests passent. Regarder `alphabet.png` : `m`, `w`, `M`, `W`, `%` et `‰` doivent être reconnaissables et de même graisse que leurs voisins.
- [ ] **Étape 5 : commit** `feat(luciole-mono): compression des glyphes larges sans perte de graisse`

### Task 4: redessin des lettres étroites et zéro barré

**Fichiers :**
- Créer : `luciole-mono/lib/narrow.py` (fonctions FontForge de dessin)
- Modifier : `luciole-mono/build.py`, `luciole-mono/config.py`
- Test : `luciole-mono/tests/test_narrow.py`

**Interfaces :**
- Produit : dans `lib/narrow.py`, `add_serif(glyph, x_from: int, x_to: int, y: int, thickness: int) -> None` dessine un rectangle et le fusionne avec le glyphe. On en tire une fonction de redessin par lettre : `redesign_i`, `redesign_j`, `redesign_l`, `redesign_I`, `redesign_one`, `redesign_r`, `redesign_f`, `redesign_t`, chacune avec la signature `(font, stem: int) -> None`. `stem` est l'épaisseur du fût de `n` dans la source, mesurée par le script lui-même.
- **Changement par rapport à la conception :** Luciole contient déjà un zéro barré dessiné par ses auteurs (`zero.slash`, activé par la feature `zero`). On l'utilise comme `0` par défaut, au lieu de dessiner un point. Concrètement : on copie les contours de `zero.slash` dans `zero` (et de `zero.slashLT` dans `zero.LT`, etc.).

- [ ] **Étape 1 : écrire les tests qui échouent**

```python
@pytest.mark.parametrize("ch", list("iljrftI1"))
def test_narrow_letters_fill_cell(font, ch):
    g = font["glyf"][font.getBestCmap()[ord(ch)]]
    assert g.xMax - g.xMin >= 0.55 * 620
@pytest.mark.parametrize("a,b", [("l","1"),("l","I"),("I","1"),("l","|"),("0","O"),("0","o")])
def test_confusables_differ(a, b):
    ia, ib = render(DIST, a, 32), render(DIST, b, 32)
    diff = sum(abs(p - q) > 128 for p, q in zip(ia.getdata(), ib.getdata()))
    ink = sum(p < 128 for p in ia.getdata())
    assert diff >= 0.25 * ink
def test_zero_is_slashed(font, source):
    ff, sf = font["glyf"], source["glyf"]
    assert ff["zero"].numberOfContours == sf["zero.slash"].numberOfContours
```

- [ ] **Étape 2 :** lancer les tests. Résultat attendu : ÉCHEC sur la largeur d'encre de `i`, `l`, `j`… et sur le zéro.
- [ ] **Étape 3 :** écrire `add_serif` et les fonctions de redessin. Formes fixées par la conception :
  - `i` et `j` : empattement d'attaque à gauche, `i` avec un pied horizontal ;
  - `l` : empattement d'attaque, terminé par une queue courbe vers la droite (on reprend la terminaison du `t` de Luciole) ;
  - `I` : empattements en haut et en bas ;
  - `1` : drapeau allongé et socle ;
  - `r`, `f`, `t` : traits horizontaux allongés ;
  - `|` n'est pas modifié.

  L'épaisseur des empattements vaut `0.85 × stem` (valeur de départ, à ajuster sur les planches). Appeler ces fonctions dans `build.py` **avant** le centrage. Remplacer ensuite les contours de `zero*` par ceux de `zero.slash*`.
- [ ] **Étape 4 :** lancer `make all specimen`. Résultat attendu : tous les tests passent. **Montrer `confusables.png` et `code.png` à l'utilisateur** et ajuster les valeurs d'après ses remarques avant de commiter.
- [ ] **Étape 5 : commit** `feat(luciole-mono): empattements des lettres étroites, zéro barré`

### Task 5: les lettres accentuées suivent les bases redessinées

**Fichiers :**
- Créer : `luciole-mono/lib/accents.py`
- Modifier : `luciole-mono/build.py`
- Test : `luciole-mono/tests/test_accents.py`

**Interfaces :**
- Produit :
  - `split_accent(accented: list[Contour], base: list[Contour]) -> tuple[list[Contour], int]` : renvoie les contours de l'accent et le décalage horizontal `dx` de la base dans le glyphe accentué. `Contour = list[tuple[int, int]]` ;
  - `derived_glyphs(cmap: dict[int,str], bases: set[str]) -> dict[str, str]` : associe chaque glyphe accentué au nom de sa base redessinée, à l'aide de `unicodedata.decomposition`. Pour `i` et `j`, la base qu'on cherche dans le glyphe accentué est `dotlessi` ou `uni0237`, puisque l'accent remplace le point.
- Algorithme (le seul qui ne découle pas des signatures) : une base se retrouve dans le glyphe accentué si ses points sont identiques à un décalage `dx` près. On teste les `dx` candidats donnés par la différence des premiers points de chaque paire de contours. Les contours qui ne correspondent pas à la base forment l'accent. Le glyphe reconstruit = la nouvelle base + l'accent décalé de `(centre du fût de la nouvelle base) − (centre du fût de l'ancienne base)`. Si un glyphe ne s'apparie pas (`ł`, `ŀ`, `ŧ`), on le laisse tel quel, simplement centré, et `build.py` affiche son nom dans un rapport.

- [ ] **Étape 1 : écrire les tests qui échouent**

```python
def test_split_accent_finds_shifted_base():
    base = [[(0,0),(10,0),(10,100),(0,100)]]
    acc  = [[(5,0),(15,0),(15,100),(5,100)], [(0,120),(20,120),(10,140)]]
    accent, dx = split_accent(acc, base)
    assert dx == 5 and accent == [acc[1]]
@pytest.mark.parametrize("ch,base", [("í","dotlessi"),("ï","dotlessi"),("ĺ","l"),("ť","t"),("ŕ","r"),("Í","I")])
def test_accented_follow_redesigned_base(font, ch, base):
    g = glyph_contours(font, font.getBestCmap()[ord(ch)])
    assert split_accent(g, glyph_contours(font, base))[1] == 0
```

- [ ] **Étape 2 :** lancer les tests. Résultat attendu : ÉCHEC (module manquant, `í` construit sur l'ancien `i`).
- [ ] **Étape 3 :** écrire `split_accent` et `derived_glyphs`, puis les brancher dans `build.py` juste après le redessin de la tâche 4. Les contours d'origine sont lus dans la source avec fontTools, avant toute modification.
- [ ] **Étape 4 :** lancer `make all specimen`. Résultat attendu : tous les tests passent, et le rapport liste les glyphes non appariés. Ajouter à `alphabet.png` une ligne `íìîïĩīĭįĵĺļľŀłŕŗřţťŧÍÌÎÏ` et la vérifier.
- [ ] **Étape 5 : commit** `feat(luciole-mono): lettres accentuées reconstruites sur les bases redessinées`

### Task 6: README, installation et validation par l'utilisateur

**Fichiers :**
- Créer : `luciole-mono/README.md`
- Modifier : `luciole-mono/Makefile` (cible `install`)

- [ ] **Étape 1 :** écrire le `README.md` : attribution CC-BY (auteurs, lien vers la licence, liste des modifications), reconstruction (`make all`), dépendances, et le gras/l'italique comme prochaine étape.
- [ ] **Étape 2 :** ajouter la cible `install`, qui copie la police dans `~/.local/share/fonts/LucioleMono/` puis lance `fc-cache -f`. Lancer `make install`. Vérifier avec `fc-list :spacing=mono family | grep "Luciole Mono"`, qui doit afficher une ligne.
- [ ] **Étape 3 :** demander à l'utilisateur d'essayer la police dans son terminal et son éditeur, puis noter ses remarques. Chaque remarque devient soit un réglage dans `config.py` / `lib/narrow.py` (on relance `make all specimen`), soit une tâche suivante.
- [ ] **Étape 4 : commit** `docs(luciole-mono): README, attribution et installation`
