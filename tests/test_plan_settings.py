from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.plan_settings import EquationSet2D

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"
MUNCIE_PRJ = TEST_DATA / "ras/Muncie.prj"


def test_EquationSet2D_a():
    assert (
        EquationSet2D().run(RasModel(BALDEAGLE_PRJ)).__dict__.__str__()
        == "{'result': <ResultStatus.OK: 'ok'>, 'name': '2D Equation Set', 'filename': 'BaldEagleDamBrk.p18.hdf', 'message': None, 'gdf': None}"
    )


def test_EquationSet2D_b():
    assert (
        EquationSet2D().run(RasModel(MUNCIE_PRJ)).__dict__.__str__()
        == "{'result': <ResultStatus.OK: 'ok'>, 'name': '2D Equation Set', 'filename': 'Muncie.p03.hdf', 'message': None, 'gdf': None}"
    )
