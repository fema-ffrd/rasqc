import pytest
from rasqc.base_checker import RasqcChecker
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult


def test_base_checker_not_implemented():
    """Test that the base checker raises NotImplementedError."""
    checker = RasqcChecker()

    # Create a minimal RasModel for testing
    TEST_DATA = "./tests/data/ras/BaldEagleDamBrk.prj"

    with pytest.raises(NotImplementedError):
        checker.run(RasModel(TEST_DATA))


class ConcreteChecker(RasqcChecker):
    """A concrete implementation of RasqcChecker for testing."""

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Implementation that returns a dummy result."""
        from rasqc.result import ResultStatus

        return RasqcResult(
            result=ResultStatus.OK,
            name="Test Checker",
            filename=ras_model.prj_file.path.name,
        )


def test_concrete_checker():
    """Test a concrete implementation of RasqcChecker."""
    checker = ConcreteChecker()

    # Create a minimal RasModel for testing
    TEST_DATA = "./tests/data/ras/BaldEagleDamBrk.prj"

    result = checker.run(RasModel(TEST_DATA))

    assert result.name == "Test Checker"
    assert result.result.value == "ok"
    assert result.filename == "BaldEagleDamBrk.prj"
