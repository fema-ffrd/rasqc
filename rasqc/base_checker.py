"""Base class for all quality control checkers."""

from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult

from typing import List


class RasqcChecker:
    """Base class for all quality control checkers.

    All specific checkers should inherit from this class and implement
    the run method to perform their specific check.

    Attributes
    ----------
        name: The name of the checker, to be overridden by subclasses.
    """

    name: str
    criteria: str

    def run(self, ras_model: RasModel) -> RasqcResult | List[RasqcResult]:
        """Run the checker on the HEC-RAS model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.

        Raises
        ------
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError()
