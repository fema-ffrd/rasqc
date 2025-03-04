from pathlib import Path
from dataclasses import asdict
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.associated_layers import AssociatedLayers

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagle/BaldEagleDamBrk.prj"


def test_AssociatedLayers():
    assert asdict(AssociatedLayers().run(RasModel(BALDEAGLE_PRJ))) == {
        "result": ResultStatus.NOTE,
        "name": "Associated Layers",
        "filename": ["BaldEagleDamBrk.g06.hdf", "BaldEagleDamBrk.g11.hdf"],
        "message": [
            {
                "Terrain": ".\\Terrain\\Terrain50.hdf",
                "Land Cover": None,
                "Infiltration": None,
            },
            {
                "Terrain": ".\\Terrain\\Terrain50.hdf",
                "Land Cover": ".\\Land Classification\\LandCover.hdf",
                "Infiltration": None,
            },
        ],
        "gdf": None,
    }
