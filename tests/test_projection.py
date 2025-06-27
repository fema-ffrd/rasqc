from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.projection import GeomProjection, NoteGeomProjection

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_GeomProjection():
    results = GeomProjection().run(RasModel(BALDEAGLE_PRJ))
    result = results[0]
    assert result.result.value == "error"


def test_GeomProjectionNote():
    assert {
        res.filename: res.to_dict()
        for res in NoteGeomProjection().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.g06.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Geometry Projection",
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
            "name": "Geometry Projection",
            "filename": "BaldEagleDamBrk.g11.hdf",
            "element": None,
            "message": "NAD83 / Pennsylvania North (ftUS)",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }
