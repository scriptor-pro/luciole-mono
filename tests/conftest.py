import sys
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config  # noqa: E402

DIST = str(ROOT / "dist" / f"{config.PS_NAME}.ttf")


@pytest.fixture(scope="session")
def font():
    return TTFont(DIST)


@pytest.fixture(scope="session")
def source():
    return TTFont(config.SOURCE)
