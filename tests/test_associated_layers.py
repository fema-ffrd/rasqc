from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.associated_layers import AssociatedLayers

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_AssociatedLayers():
    assert {
        res.filename: res.to_dict()
        for res in AssociatedLayers().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.g06.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Associated Layers",
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
            "name": "Associated Layers",
            "filename": "BaldEagleDamBrk.g11.hdf",
            "element": None,
            "message": '{"terrain": ".\\\\Terrain\\\\Terrain50.hdf", "land cover": ".\\\\Land Classification\\\\LandCover.hdf", "infiltration": null}',
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }
