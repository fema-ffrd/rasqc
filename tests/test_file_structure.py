from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.file_structure import FileStructure
from rasqc.result import ResultStatus

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_CurrentPlan():
    assert FileStructure().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "File Structure",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"title": "Bald Eagle Creek Example Dam Break Study", "plans": {"BaldEagleDamBrk.p13": {"title": "PMF with Multi 2D Areas", "geometry": {"BaldEagleDamBrk.g06": {"title": "Bald Eagle Multi 2D Areas"}}, "unsteady": {"BaldEagleDamBrk.u07": {"title": "PMF with Multi 2D Areas"}}}, "BaldEagleDamBrk.p18": {"title": "2D to 2D Run", "geometry": {"BaldEagleDamBrk.g11": {"title": "2D to 2D Connection"}}, "unsteady": {"BaldEagleDamBrk.u10": {"title": "1972 Flood Event - 2D to 2D Run"}}}}}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }
