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
                "terrain": ".\\Terrain\\Terrain50.hdf",
                "land cover": None,
                "infiltration": None,
            },
            {
                "terrain": ".\\Terrain\\Terrain50.hdf",
                "land cover": ".\\Land Classification\\LandCover.hdf",
                "infiltration": None,
            },
        ],
        "gdf": None,
    }
