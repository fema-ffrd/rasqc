"""Plan settings checkers for FFRD HEC-RAS models."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from rashdf import RasPlanHdf

from pathlib import Path
from typing import List


@register_check(["ffrd"], dependencies=["PlanHdfExists"])
class EquationSet2D(RasqcChecker):
    """Checker for 2D equation set settings.

    Checks if the 2D equation set is set to 'Diffusion Wave' as required
    for FFRD models.
    """

    name = "2D Equation Set"

    def _check(self, phdf: RasPlanHdf, phdf_filename: str) -> List[RasqcResult]:
        """Check if the 2D equation set is set to 'Diffusion Wave'.

        Parameters
        ----------
            phdf: The HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        plan_params = phdf.get_plan_param_attrs()
        equation_sets = (
            [plan_params["2D Equation Set"]]
            if isinstance(plan_params["2D Equation Set"], str)
            else plan_params["2D Equation Set"]
        )
        results = []
        for equation_set in equation_sets:
            if equation_set != "Diffusion Wave":
                results.append(
                    RasqcResult(
                        name=self.name,
                        result=ResultStatus.WARNING,
                        filename=phdf_filename,
                        message=(
                            f"2D Equation Set '{equation_set}'"
                            " does not match expected setting: 'Diffusion Wave'."
                        ),
                    )
                )
            else:
                results.append(
                    RasqcResult(
                        name=self.name,
                        result=ResultStatus.OK,
                        filename=phdf_filename,
                    )
                )
        return results

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the 2D equation set is set to 'Diffusion Wave'.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        results = []
        for plan in ras_model.plans:
            if plan.hdf:
                phdf_filename = Path(plan._hdf_path).name
                results.extend(self._check(plan.hdf, phdf_filename))
        return results
