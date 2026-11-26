import specimen
from conftest import DIST
from render import ink_runs


def test_specimens_written(tmp_path):
    specimen.main(out_dir=tmp_path)
    for name in ("alphabet.png", "confusables.png", "code.png", "vs-atkinson.png",
                 "accents.png"):
        assert (tmp_path / name).stat().st_size > 0


def test_ink_runs_n_has_two_stems():
    assert len(ink_runs(DIST, "n", 270)) == 2


def test_pango_renders_the_given_file():
    """Les planches passent par Pango (comme les applications du bureau) et
    rendent bien le fichier demandé, pas une police installée du même nom :
    le 0 barré de Luciole Mono diffère du 0 de Luciole."""
    import config
    from conftest import DIST
    from lib.pango_render import render_pango
    mono, source = render_pango(DIST, "0", 48), render_pango(config.SOURCE, "0", 48)
    assert mono.getbbox() is not None and min(mono.tobytes()) < 64
    assert mono.tobytes() != source.tobytes()
