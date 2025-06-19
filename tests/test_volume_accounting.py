from pathlib import Path

from rasqc.rasmodel import RasModel
from rasqc.checkers.volume_accounting import VolumeError
from rasqc.result import ResultStatus

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_VolumeError():
    assert {
        res.filename: res.to_dict()
        for res in VolumeError().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.WARNING,
            "name": "Volume Accounting Error",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "Plan HDF file not found.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.OK,
            "name": "Volume Accounting Error",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": None,
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }
