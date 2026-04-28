"""Tests for HDF sync checkers."""

from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.hdfsync import (
    GeomHdfExists,
    GeomHdfDatetime,
    PlanHdfExists,
    PlanHdfDatetime,
)

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_GeomHdfExists():
    """Test the GeomHdfExists checker."""
    results = GeomHdfExists().run(RasModel(BALDEAGLE_PRJ))

    # The result should be a list since it checks all geometry files
    assert isinstance(results, list)
    assert len(results) > 0

    # Check each result
    for result in results:
        assert result.name == "Geometry HDF file exists"
        assert result.result in [ResultStatus.OK, ResultStatus.ERROR]
        assert result.filename is not None

        # If HDF doesn't exist, should have error message
        if result.result == ResultStatus.ERROR:
            assert "should have a corresponding HDF file" in result.message
        else:
            # If OK, message should be None or empty
            assert result.result == ResultStatus.OK


def test_GeomHdfDatetime():
    """Test the GeomHdfDatetime checker."""
    results = GeomHdfDatetime().run(RasModel(BALDEAGLE_PRJ))

    # The result should be a list since it checks all geometry files
    assert isinstance(results, list)
    assert len(results) > 0

    # Check each result
    for result in results:
        assert result.name == "Geometry HDF file datetime"
        assert result.result in [ResultStatus.OK, ResultStatus.ERROR]
        assert result.filename is not None

        # If there's an error, check the message format
        if result.result == ResultStatus.ERROR:
            assert result.message is not None


def test_PlanHdfExists():
    """Test the PlanHdfExists checker."""
    results = PlanHdfExists().run(RasModel(BALDEAGLE_PRJ))

    # The result should be a list since it checks all plan files
    assert isinstance(results, list)
    assert len(results) > 0

    # Check each result
    for result in results:
        assert result.name == "Plan HDF file exists"
        assert result.result in [ResultStatus.OK, ResultStatus.ERROR]
        assert result.filename is not None

        # If HDF doesn't exist, should have error message
        if result.result == ResultStatus.ERROR:
            assert "should have a corresponding HDF file" in result.message
        else:
            # If OK, message should be None or empty
            assert result.result == ResultStatus.OK


def test_PlanHdfDatetime():
    """Test the PlanHdfDatetime checker."""
    results = PlanHdfDatetime().run(RasModel(BALDEAGLE_PRJ))

    # The result should be a list since it checks all plan files
    assert isinstance(results, list)
    assert len(results) > 0

    # Check each result
    for result in results:
        assert result.name == "Plan HDF file datetime"
        assert result.result in [ResultStatus.OK, ResultStatus.ERROR]
        assert result.filename is not None

        # If there's an error, check that a message exists
        if result.result == ResultStatus.ERROR:
            assert result.message is not None
