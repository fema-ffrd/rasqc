from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.projection import GeomProjection

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_GeomProjection():
    results = GeomProjection().run(RasModel(BALDEAGLE_PRJ))
    result = results[0]
    assert result.result.value == "error"
