from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.file_structure import FileStructure
from rasqc.result import ResultStatus

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_FileStructure():
    assert FileStructure().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "File Structure",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"filename": "BaldEagleDamBrk.prj", "title": "Bald Eagle Creek Example Dam Break Study", "description": "", "plans": {"p13": {"filename": "BaldEagleDamBrk.p13", "title": "PMF with Multi 2D Areas", "short id": "PMF Multi 2D", "description": "", "geometry": {"filename": "BaldEagleDamBrk.g06", "title": "Bald Eagle Multi 2D Areas", "description": ""}, "unsteady": {"filename": "BaldEagleDamBrk.u07", "title": "PMF with Multi 2D Areas", "description": ""}}, "p18": {"filename": "BaldEagleDamBrk.p18", "title": "2D to 2D Run", "short id": "2D to 2D Run", "description": "", "geometry": {"filename": "BaldEagleDamBrk.g11", "title": "2D to 2D Connection", "description": ""}, "unsteady": {"filename": "BaldEagleDamBrk.u10", "title": "1972 Flood Event - 2D to 2D Run", "description": ""}}}}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }
