from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult


class RasqcChecker:
    """Base class for all checkers."""

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Run the checker on the HEC-RAS model."""
        raise NotImplementedError()
