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
                phdf_filename = Path(plan.hdf_path).name
                results.extend(self._check(plan.hdf, phdf_filename))
        return results


@register_check(["ble"])
class EquationSet2DNote(RasqcChecker):
    name = "2D Equation Set"

    def run(self, ras_model: RasModel) -> RasqcResult:
        filenames = []
        messages = []
        for plan_hdf_path in ras_model.plan_hdf_paths:
            filenames.append(plan_hdf_path.name)
            if not plan_hdf_path.exists():
                messages.append(
                    f"{plan_hdf_path.name} does not exist within the specified directory"
                )
            else:
                plan_hdf = RasPlanHdf(plan_hdf_path)
                plan_params = plan_hdf.get_plan_param_attrs()
                messages.append(
                    {
                        n: e
                        for n, e in zip(
                            plan_params["2D Names"], plan_params["2D Equation Set"]
                        )
                    }
                    if not isinstance(plan_params["2D Names"], (str, int, float))
                    else plan_params["2D Equation Set"]
                )
        return RasqcResult(
            name=self.name,
            filename=filenames,
            result=ResultStatus.NOTE,
            message=messages,
        )


@register_check(["ble"])
class CompSettings(RasqcChecker):
    name = "Computation Settings"

    def run(self, ras_model: RasModel) -> RasqcResult:
        settings = [
            "Computation Time Step Base",
            "Computation Time Courant Method",
            "Computation Time Step Max Courant",
            "Computation Time Step Min Courant",
            "Computation Time Step Count To Double",
            "Computation Time Step Max Doubling",
            "Computation Time Step Max Halving",
            "Time Window",
        ]
        filenames = []
        messages = []
        for plan_hdf_path in ras_model.plan_hdf_paths:
            filenames.append(plan_hdf_path.name)
            if not plan_hdf_path.exists():
                messages.append(
                    f"{plan_hdf_path.name} does not exist within the specified directory"
                )
            else:
                plan_hdf = RasPlanHdf(plan_hdf_path)
                plan_info = plan_hdf.get_plan_info_attrs()
                messages.append(
                    {
                        setting.lower(): plan_info[setting]
                        for setting in settings
                        if setting in plan_info
                    }
                )
        return RasqcResult(
            name=self.name,
            filename=filenames,
            result=ResultStatus.NOTE,
            message=messages,
        )
