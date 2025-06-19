from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.breaklines import BreaklineEnforcement

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_BreaklineEnforcement():
    res = BreaklineEnforcement().run(RasModel(BALDEAGLE_PRJ))
    assert res.message == "6 breakline enforcement flags found"
