import specimen
from conftest import DIST
from render import ink_runs


def test_specimens_written(tmp_path):
    specimen.main(out_dir=tmp_path)
    for name in ("alphabet.png", "confusables.png", "code.png", "vs-atkinson.png"):
        assert (tmp_path / name).stat().st_size > 0


def test_ink_runs_n_has_two_stems():
    assert len(ink_runs(DIST, "n", 270)) == 2
