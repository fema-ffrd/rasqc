from pathlib import Path

from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.structures import BridgeXsData, OverflowMethod

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_BridgeXsData():
    assert {
        res.filename: res.to_dict()
        for res in BridgeXsData().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.g06": {
            "result": ResultStatus.OK,
            "name": "Bridge XS Data",
            "filename": "BaldEagleDamBrk.g06",
            "element": None,
            "message": "No bridges located within geometry.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.g11": {
            "result": ResultStatus.OK,
            "name": "Bridge XS Data",
            "filename": "BaldEagleDamBrk.g11",
            "element": None,
            "message": "No bridges located within geometry.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }


def test_OverflowMethod():
    assert (
        OverflowMethod().run(RasModel(BALDEAGLE_PRJ)).message
        == "any applicable structures found use 2d for overflow comps"
    )
