# Luciole Mono

*[Français](README.fr.md)* · Website: https://scriptor-pro.github.io/luciole-mono/

A monospaced version of the **Luciole** typeface, for terminals and code editors.

Luciole was designed for visually impaired readers by Laurent Bourcellier and Jonathan Perez (Centre Technique Régional pour la Déficience Visuelle, [typographies.fr](https://typographies.fr)). Luciole Mono keeps its design and fits it to a grid where every character has the same width.

**Luciole Mono is a derivative of Luciole.** It is an independent project, neither made nor endorsed by the authors of Luciole.

## Install

Ready-to-use fonts are in [`dist/`](dist): `LucioleMono-Regular.ttf`, `-Bold.ttf`, `-Italic.ttf`, `-BoldItalic.ttf`.

- **Linux**: copy the four files to `~/.local/share/fonts/`, then run `fc-cache -f`.
- **macOS, Windows**: open each file and choose "Install".

Then pick "Luciole Mono" in your terminal or editor. 11 pt (15 px) renders particularly crisply.

## License and attribution

Luciole © Laurent Bourcellier & Jonathan Perez – 2019, released under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/legalcode) license. The original Luciole files (version 1.001) used by the build scripts are included unmodified in [`sources/luciole/`](sources/luciole).

The whole repository (Luciole Mono fonts and build scripts) is released under **the same license, CC-BY 4.0**: see [`LICENSE`](LICENSE). When reusing it, credit Luciole (Laurent Bourcellier & Jonathan Perez) and Luciole Mono.

Luciole Mono (Regular, Bold, Italic and Bold Italic) is a **derivative work** of Luciole Regular. Changes made:

- every glyph is 620 units wide (1000 units per em);
- wide glyphs (`m`, `w`, `M`, `W`, `@`…) are compressed, then thickened horizontally to restore their stroke weight, without ever closing their inner spaces. In Regular, the stems of `m` are kept as they are (`condenseExtend`);
- `i`, `j`, `l` and `r` are redrawn with serifs (and a curved tail for `l`) to fill the cell and avoid confusion;
- accented letters built on these bases are rebuilt;
- `%` and `‰` are redrawn: their rings are smaller but stay round, on either side of the slash;
- Luciole's slashed zero (`zero.slash`) becomes the default `0`, narrower than `O`;
- the bold is a **semi-bold** made from Luciole Regular (`make_source.py`): every stroke is thickened by 44 units (stems of 156, between Regular's 112 and Luciole Bold's 200), each accent separately so it keeps its distance from the letter. Luciole Bold filled the cell too much (closed `0`, cramped `m M W`); the semi-bold also has every character of the Regular;
- in bold, `I` and `0` are narrowed to stay distinct from `1` and `O`;
- Italic and Bold Italic are the upright styles slanted by 15°, like Luciole Italic (an oblique of the upright): they keep all the redesigns above;
- when thickening, accents are not thickened and the parts of a glyph stay apart (diaeresis dots, the dots of `…`, the chevrons of `«`);
- the bold weight is declared as 700, so terminals and editors use it for bold text;
- kerning (`kern`), ligatures (`liga`) and TrueType hinting were removed, and the metadata are those of a monospaced font.

## Build

Requirements: FontForge (≥ 20230101), Pango (`pango-view`, for specimens), Python 3, and `fonttools`, `pillow`, `pytest` in `.venv`:

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
make all         # for each weight: source (make_source.py, bold only),
                 # FontForge → dist/LucioleMono-<weight>.ttf,
                 # then italicize.py (Italic, BoldItalic), then the tests
make specimen    # proof sheets in specimens/
make install     # copies to ~/.local/share/fonts/LucioleMono/ and runs fc-cache
```

Settings (cell width, margin, thickening, bold-specific tweaks) are in `config.py`. Dimensions (stem, `t` bar, heights) are measured on each source font (`lib/geometry.py`). Redrawn shapes are in `lib/narrow.py` and `lib/symbols.py`. The slant (`SLANT`, `SLANT_Y0`) is in `config.py`, applied by `italicize.py`. To build a single weight: `make all STYLES=Bold` (only its italic is rebuilt).

Code comments and test messages are in French.

## Known limitations

- In bold, `M`, `W`, `w` and wide symbols are lighter than other bold letters: thickening stops before it would close their notches (bottom of `M`). `%` and `‰` are almost as light as Regular (their rings are limited by their counters).
- `⇔` is hard to read in both weights.
- In bold, a few rare glyphs still have touching parts: fractions (`½ ¼ ¾`…), typographic ligatures (`ﬁ ﬂ ﬀ`…) and `℗`. Fractions and `№` are slightly lighter than their neighbours, to stay legible.
- The diagonals of thickened wide glyphs show small steps at large sizes.
- Italics slightly overflow the cell at the top right and bottom left, like any monospaced italic.
- `ł`, `į`, `ⁱ` and `ℓ` keep their original, centred design: their accent is joined to the letter in Luciole.
- At small sizes (11 pt), `℗` looks like the slashed zero, and `‰` reads almost like "%.".
