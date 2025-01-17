from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.projection import GeomProjection

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_GeomProjection():
    assert (
        GeomProjection().run(RasModel(BALDEAGLE_PRJ)).message
        == "HEC-RAS geometry HDF file projection 'NAD83 / Pennsylvania North (ftUS)' does not match the expected projection for FFRD models. (BaldEagleDamBrk.g11.hdf)"
    )
