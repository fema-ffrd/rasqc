from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.current_plan import NoteCurrentPlan

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_CurrentPlan():
    assert NoteCurrentPlan().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "Current Saved Plan",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"file": "BaldEagleDamBrk.p18", "title": "2D to 2D Run"}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }
