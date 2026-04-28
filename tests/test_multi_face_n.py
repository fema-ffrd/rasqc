"""Tests for the MultiFaceManningN checker."""

from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.multi_face_n import MultiFaceManningN

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_MultiFaceManningN():
    """Test the MultiFaceManningN checker for multiple face Manning's n setting."""
    result = MultiFaceManningN().run(RasModel(BALDEAGLE_PRJ))

    # The result should be a list since it checks all geometries
    assert isinstance(result, list)
    assert len(result) > 0

    # Check the first result
    first_result = result[0]
    assert first_result.name == "Multiple Face Manning's n"
    assert first_result.result in [ResultStatus.NOTE, ResultStatus.WARNING]
    assert first_result.filename is not None
    assert first_result.message is not None

    # If HDF file not found, result should be WARNING
    if "not found" in first_result.message.lower():
        assert first_result.result == ResultStatus.WARNING
    # If Multiple Face Mann n is enabled, result should be NOTE
    elif first_result.result == ResultStatus.NOTE:
        assert "enabled" in first_result.message.lower()
    # If Multiple Face Mann n is NOT enabled, result should be WARNING
    elif first_result.result == ResultStatus.WARNING:
        assert "not enabled" in first_result.message.lower()
