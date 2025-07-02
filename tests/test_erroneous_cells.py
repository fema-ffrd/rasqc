from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.erroneous_cells import ErroneousCells

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_BreaklineEnforcement():
    assert ErroneousCells().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.OK,
        "name": "Erroneous Cells",
        "filename": "BaldEagleDamBrk.g11.hdf",
        "element": None,
        "message": "no erroneous cells found",
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }
