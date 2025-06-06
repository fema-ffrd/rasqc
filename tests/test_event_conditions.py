from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.event_conditions import MeteorologyPrecip
from rasqc.result import ResultStatus

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_MeteorologyPrecip():
    assert MeteorologyPrecip().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "Meteorology Precipitation",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"p13 (PMF with Multi 2D Areas)": "No HDF file located.", "p18 (2D to 2D Run)": "No meteorology precip applied."}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }
