"""Tests for the WaterSurfaceError checker."""

from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.ws_error import WaterSurfaceError

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_WaterSurfaceError():
    """Test the WaterSurfaceError checker for computational errors."""
    result = WaterSurfaceError().run(RasModel(BALDEAGLE_PRJ))

    # The result should be a list since it checks all plan files
    assert isinstance(result, list)
    assert len(result) > 0

    # Check the first result
    first_result = result[0]
    assert first_result.name == "Water Surface Error"
    assert first_result.result in [
        ResultStatus.OK,
        ResultStatus.ERROR,
        ResultStatus.WARNING,
    ]
    assert first_result.filename is not None
    assert first_result.message is not None

    # If there are error flags, ensure the GeoDataFrame is returned
    if first_result.result == ResultStatus.ERROR:
        assert first_result.gdf is not None
        assert not first_result.gdf.empty
        assert "max_ws_err" in first_result.gdf.columns
        assert "water surface errors exceeding" in first_result.message

    # If result is OK, verify the message
    if first_result.result == ResultStatus.OK:
        assert "within limits" in first_result.message.lower()
