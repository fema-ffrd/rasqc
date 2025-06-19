from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.projection import GeomProjection

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_GeomProjection():
    results = GeomProjection().run(RasModel(BALDEAGLE_PRJ))
    result = results[0]
    assert result.result.value == "error"


def test_GeomProjectionNote():
    assert (
        json.dumps(
            asdict(GeomProjectionNote().run(RasModel(BALDEAGLE_PRJ))),
            cls=RasqcResultEncoder,
        )
        == '{"result": "note", "name": "Geometry Projection", "filename": "BaldEagleDamBrk.g11.hdf", "message": "NAD83 / Pennsylvania North (ftUS)", "gdf": null}'
    )
