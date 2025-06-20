from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.ras_version import RasVersion

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_RasVersion():
    assert {
        res.filename: res.to_dict() for res in RasVersion().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.g06.hdf": {
            "result": ResultStatus.NOTE,
            "name": "HEC-RAS Version",
            "filename": "BaldEagleDamBrk.g06.hdf",
            "element": None,
            "message": "Geometry HDF file not found.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.g11.hdf": {
            "result": ResultStatus.NOTE,
            "name": "HEC-RAS Version",
            "filename": "BaldEagleDamBrk.g11.hdf",
            "element": None,
            "message": "HEC-RAS 6.5 February 2024",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }
