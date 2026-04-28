"""Tests for the ErroneousFaces checker."""

from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.erroneous_faces import ErroneousFaces

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_ErroneousFaces():
    """Test the ErroneousFaces checker for mesh faces with sharp angles."""
    result = ErroneousFaces().run(RasModel(BALDEAGLE_PRJ))

    assert result.name == "Erroneous Faces"
    assert result.result in [ResultStatus.OK, ResultStatus.ERROR, ResultStatus.WARNING]
    assert result.filename is not None
    assert result.message is not None

    # If there are erroneous faces, ensure the GeoDataFrame is returned
    if result.result == ResultStatus.ERROR:
        assert result.gdf is not None
        assert not result.gdf.empty
        assert "min_angle" in result.gdf.columns
        assert "geometry" in result.gdf.columns
        assert "erroneous faces found" in result.message
        # Verify all flagged faces have angles less than 75 degrees
        assert (result.gdf["min_angle"] < 75).all()

    # If result is OK, verify the message
    if result.result == ResultStatus.OK:
        assert result.message == "no erroneous faces found"
        assert result.gdf is None
