from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.plan_settings import EquationSet2D

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"
MUNCIE_PRJ = TEST_DATA / "ras/Muncie.prj"


def test_EquationSet2D_a():
    results = EquationSet2D().run(RasModel(BALDEAGLE_PRJ))
    result = results[0]
    assert result.result.value == "ok"


def test_EquationSet2D_b():
    results = EquationSet2D().run(RasModel(MUNCIE_PRJ))
    result = results[0]
    assert result.result.value == "ok"
