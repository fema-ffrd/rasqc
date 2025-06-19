"""Checks related to the current saved plan within a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus


@register_check(["ble"])
class CurrentPlan(RasqcChecker):
    """Checker for the current saved plan.

    Reports the name and title of the plan saved as the current plan within a RAS model.
    """

    name = "Current Saved Plan"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Check the current saved plan for a HEC-RAS model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message={
                "file": ras_model.current_plan.path.name,
                "title": ras_model.current_plan.title,
            },
        )
