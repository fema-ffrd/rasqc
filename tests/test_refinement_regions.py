from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.refinement_regions import RefRegionEnforcement

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_RefRegionEnforcement():
    res = RefRegionEnforcement().run(RasModel(BALDEAGLE_PRJ))
    assert res.message == "no refinement regions found within the model geometry"
