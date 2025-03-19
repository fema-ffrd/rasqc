from rasqc.registry import CHECKSUITES, register_check
from rasqc.checksuite import CheckSuite, _bold_single_quotes
from rasqc.base_checker import RasqcChecker
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus
from pathlib import Path
import pytest


class MockChecker(RasqcChecker):
    name = "Mock Checker"

    def run(self, ras_model: RasModel) -> RasqcResult:
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.OK,
        )


class MockErrorChecker(RasqcChecker):
    name = "Mock Error Checker"

    def run(self, ras_model: RasModel) -> RasqcResult:
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.ERROR,
            message="This is an 'error' message",
        )


class MockWarningChecker(RasqcChecker):
    name = "Mock Warning Checker"

    def run(self, ras_model: RasModel) -> RasqcResult:
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.WARNING,
            message="This is a 'warning' message",
        )


def test_checksuite_add_check():
    """Test adding checks to a CheckSuite."""
    suite = CheckSuite()
    suite.add_check(MockChecker())
    assert len(suite.checks) == 1
    assert isinstance(suite.checks[0], MockChecker)


def test_checksuite_run_all_silent():
    """Test running all checks silently."""
    suite = CheckSuite()
    suite.add_check(MockChecker())
    suite.add_check(MockErrorChecker())

    TEST_DATA = Path("./tests/data")
    BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"

    results = suite.run_checks(BALDEAGLE_PRJ)

    assert len(results) == 2
    assert results[0].result == ResultStatus.OK
    assert results[1].result == ResultStatus.ERROR


def test_register_check():
    """Test check registration decorator."""
    # Create a temporary checksuite for testing
    original_checksuites = CHECKSUITES.copy()
    CHECKSUITES["test_suite"] = CheckSuite()

    try:

        @register_check(["test_suite"])
        class TestChecker(RasqcChecker):
            name = "Test Checker"

            def run(self, ras_model: RasModel) -> RasqcResult:
                return RasqcResult(
                    name=self.name,
                    filename=ras_model.prj_file.path.name,
                    result=ResultStatus.OK,
                )

        assert len(CHECKSUITES["test_suite"].checks) == 1
        assert CHECKSUITES["test_suite"].checks[0].name == "Test Checker"

    finally:
        # Restore original checksuites
        CHECKSUITES.clear()
        CHECKSUITES.update(original_checksuites)


def test_register_check_invalid_suite():
    """Test registration with invalid suite name."""
    with pytest.raises(ValueError):

        @register_check(["nonexistent_suite"])
        class TestChecker(RasqcChecker):
            name = "Test Checker"

            def run(self, ras_model: RasModel) -> RasqcResult:
                return RasqcResult(
                    name=self.name,
                    filename=ras_model.prj_file.path.name,
                    result=ResultStatus.OK,
                )


def test_bold_single_quotes():
    """Test the bold_single_quotes function."""
    text = "This is a 'test' with 'multiple' quotes"
    result = _bold_single_quotes(text)
    assert (
        result
        == "This is a [bold cyan]'test'[/bold cyan] with [bold cyan]'multiple'[/bold cyan] quotes"
    )
