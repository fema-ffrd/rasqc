from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.plan_settings import EquationSet2D

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"

def test_EquationSet2D():
    assert EquationSet2D().run(RasModel(BALDEAGLE_PRJ)).__dict__.__str__() == "{'result': <ResultStatus.OK: 'ok'>, 'name': '2D Equation Set', 'filename': 'BaldEagleDamBrk.p18.hdf', 'message': None, 'gdf': None}"
