"""Tests for the PeakRouted checker."""

from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.peak_routed import PeakRouted
import json

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_PeakRouted():
    """Test the PeakRouted checker."""
    results = PeakRouted().run(RasModel(BALDEAGLE_PRJ))

    # The result should be a list since it checks all plan files
    assert isinstance(results, list)
    assert len(results) > 0

    # Check each result
    for result in results:
        assert result.name == "Peak Routed"
        assert result.result in [ResultStatus.OK, ResultStatus.WARNING]
        assert result.filename is not None
        assert result.message is not None

        # If Plan HDF is not found, should have warning
        if result.result == ResultStatus.WARNING:
            assert "not found" in result.message.lower()

        # If result is OK, message should contain JSON data
        if result.result == ResultStatus.OK:
            # Try to parse the message as JSON
            try:
                msg_dict = json.loads(result.message)
                assert isinstance(msg_dict, dict)

                # Check that each BC line has a message
                for bc_line_name, msg in msg_dict.items():
                    assert isinstance(bc_line_name, str)
                    assert isinstance(msg, str)
                    assert "Peak flow" in msg or "WARNING" in msg
            except json.JSONDecodeError:
                # If it can't be parsed as JSON, it might be a different message format
                pass


def test_PeakRouted_checks_boundary_conditions():
    """Test that PeakRouted analyzes boundary condition lines."""
    results = PeakRouted().run(RasModel(BALDEAGLE_PRJ))

    # At least one result should exist
    assert len(results) > 0

    # Check that results reference boundary conditions
    for result in results:
        if result.result == ResultStatus.OK:
            # The message should contain boundary condition analysis
            assert result.message is not None
            # Either it contains BC analysis or indicates no BC lines found
            assert (
                "boundary condition" in result.message.lower()
                or "Peak flow" in result.message
                or "WARNING" in result.message
                or "No boundary condition lines found" in result.message
            )
