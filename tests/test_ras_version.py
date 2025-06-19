from pathlib import Path
from dataclasses import asdict
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.ras_version import RasVersion

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagle/BaldEagleDamBrk.prj"


def test_RasVersion():
    assert asdict(RasVersion().run(RasModel(BALDEAGLE_PRJ))) == {
        "result": ResultStatus.NOTE,
        "name": "HEC-RAS Version",
        "filename": ["BaldEagleDamBrk.g06.hdf", "BaldEagleDamBrk.g11.hdf"],
        "message": ["HEC-RAS 6.5 February 2024", "HEC-RAS 6.5 February 2024"],
        "gdf": None,
    }
