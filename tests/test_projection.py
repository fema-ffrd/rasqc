from pathlib import Path
import json
from dataclasses import asdict
from rasqc.rasmodel import RasModel
from rasqc.checkers.projection import GeomProjection, GeomProjectionNote
from rasqc.result import RasqcResultEncoder

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagle/BaldEagleDamBrk.prj"


def test_GeomProjection():
    assert (
        GeomProjection().run(RasModel(BALDEAGLE_PRJ)).message
        == "HEC-RAS geometry HDF file projection 'NAD83 / Pennsylvania North (ftUS)' does not match the expected projection for FFRD models. (BaldEagleDamBrk.g11.hdf)"
    )


def test_GeomProjectionNote():
    assert (
        json.dumps(
            asdict(GeomProjectionNote().run(RasModel(BALDEAGLE_PRJ))),
            cls=RasqcResultEncoder,
        )
        == '{"result": "note", "name": "Geometry Projection", "filename": "BaldEagleDamBrk.g11.hdf", "message": "HEC-RAS geometry HDF file projection: \'NAD83 / Pennsylvania North (ftUS)\'", "gdf": null}'
    )
