from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.naming import (
    PrjFilenamePattern,
)

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_PrjFilenamePattern():
    assert PrjFilenamePattern().run(RasModel(BALDEAGLE_PRJ)).result.value == "error"
