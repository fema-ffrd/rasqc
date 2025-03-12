from pathlib import Path
from dataclasses import asdict
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.file_structure import FileStructure

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagle/BaldEagleDamBrk.prj"


def test_CurrentPlan():
    assert asdict(FileStructure().run(RasModel(BALDEAGLE_PRJ))) == {
        "result": ResultStatus.NOTE,
        "name": "File Structure",
        "filename": "BaldEagleDamBrk.prj",
        "message": {
            "title": "Bald Eagle Creek Example Dam Break Study",
            "plans": {
                "BaldEagleDamBrk.p13": {
                    "title": "PMF with Multi 2D Areas",
                    "geometry": {"BaldEagleDamBrk.g06": "Bald Eagle Multi 2D Areas"},
                    "unsteady": {"BaldEagleDamBrk.u07": "PMF with Multi 2D Areas"},
                },
                "BaldEagleDamBrk.p18": {
                    "title": "2D to 2D Run",
                    "geometry": {"BaldEagleDamBrk.g11": "2D to 2D Connection"},
                    "unsteady": {
                        "BaldEagleDamBrk.u10": "1972 Flood Event - 2D to 2D Run"
                    },
                },
            },
        },
        "gdf": None,
    }
