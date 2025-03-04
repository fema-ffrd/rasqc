from pathlib import Path
from dataclasses import asdict
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.current_plan import CurrentPlan

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagle/BaldEagleDamBrk.prj"


def test_CurrentPlan():
    assert asdict(CurrentPlan().run(RasModel(BALDEAGLE_PRJ))) == {
        "result": ResultStatus.NOTE,
        "name": "Current Saved Plan",
        "filename": "BaldEagleDamBrk.prj",
        "message": {"File": "BaldEagleDamBrk.p18", "Title": "2D to 2D Run"},
        "gdf": None,
    }
