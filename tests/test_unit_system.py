"""Tests for the NoteUnitSystem checker."""

from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.unit_system import NoteUnitSystem

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_NoteUnitSystem():
    """Test the NoteUnitSystem checker."""
    results = NoteUnitSystem().run(RasModel(BALDEAGLE_PRJ))

    # The result should be a list since it checks all plan files
    assert isinstance(results, list)
    assert len(results) > 0

    # Check each result
    for result in results:
        assert result.name == "Unit System"
        assert result.result in [ResultStatus.NOTE, ResultStatus.WARNING]
        assert result.filename is not None
        assert result.message is not None

        # If Plan HDF is not found, should have warning
        if result.result == ResultStatus.WARNING:
            assert "not found" in result.message

        # If result is NOTE, message should contain unit system info
        if result.result == ResultStatus.NOTE:
            # The message should indicate the unit system
            # Common values: "SI Units", "English Units"
            assert len(result.message) > 0


def test_NoteUnitSystem_returns_valid_units():
    """Test that NoteUnitSystem returns valid unit system information."""
    results = NoteUnitSystem().run(RasModel(BALDEAGLE_PRJ))

    # At least one result should exist
    assert len(results) > 0

    # Check that results contain unit system information
    has_note_result = False
    for result in results:
        if result.result == ResultStatus.NOTE:
            has_note_result = True
            # The message should not be empty for NOTE results
            assert result.message
            # Common unit system values
            assert (
                result.message
                in [
                    "SI Units",
                    "US Customary",
                ]
                or "Unit" in result.message
            )

    # At least one result should have NOTE status with valid units
    # (unless all plans don't have HDF files)
    if not has_note_result:
        # All results should be WARNING about missing HDF files
        for result in results:
            assert result.result == ResultStatus.WARNING
            assert "not found" in result.message


def test_NoteUnitSystem_handles_missing_hdf():
    """Test that NoteUnitSystem handles missing HDF files gracefully."""
    results = NoteUnitSystem().run(RasModel(BALDEAGLE_PRJ))

    # Should return results for all plans
    assert len(results) > 0

    # Check that missing HDF files are handled
    for result in results:
        assert result.result in [ResultStatus.NOTE, ResultStatus.WARNING]
        # Should not raise an exception
        assert result.message is not None
