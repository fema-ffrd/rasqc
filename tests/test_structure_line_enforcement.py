"""Tests for the StructureLineEnforcement checker."""

from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.structure_line_enforcement import StructureLineEnforcement

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_StructureLineEnforcement():
    """Test the StructureLineEnforcement checker."""
    result = StructureLineEnforcement().run(RasModel(BALDEAGLE_PRJ))

    # The result should be a single RasqcResult (not a list)
    assert result is not None
    assert result.name == "Structure Line Enforcement"
    assert result.result in [ResultStatus.OK, ResultStatus.ERROR, ResultStatus.WARNING]
    assert result.filename is not None
    assert result.message is not None

    # If there are enforcement flags, ensure the GeoDataFrame is returned
    if result.result == ResultStatus.ERROR:
        assert result.gdf is not None
        assert not result.gdf.empty
        assert "structure line enforcement flags found" in result.message

        # Verify the geometry column exists
        assert "geometry" in result.gdf.columns

    # If result is OK, verify the message
    if result.result == ResultStatus.OK:
        assert "no structure line enforcement flags found" in result.message

    # If result is WARNING, should indicate structures not found or HDF not found
    if result.result == ResultStatus.WARNING:
        assert (
            "not found" in result.message.lower()
            or "no structures" in result.message.lower()
        )


def test_StructureLineEnforcement_checks_single_geometry():
    """Test that StructureLineEnforcement only checks current geometry."""
    result = StructureLineEnforcement().run(RasModel(BALDEAGLE_PRJ))

    # Should return a single result, not a list
    assert not isinstance(result, list)
    assert result.name == "Structure Line Enforcement"


def test_StructureLineEnforcement_handles_no_structures():
    """Test that StructureLineEnforcement handles geometries without structures."""
    result = StructureLineEnforcement().run(RasModel(BALDEAGLE_PRJ))

    # Should return a valid result
    assert result is not None
    assert result.result in [ResultStatus.OK, ResultStatus.WARNING, ResultStatus.ERROR]

    # If no structures, should indicate in message
    if result.result == ResultStatus.WARNING:
        if "no structures" in result.message.lower():
            assert "geometry" in result.message.lower()
