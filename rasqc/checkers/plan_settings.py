"""Plan settings checkers for FFRD HEC-RAS models."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus, RasqcResultEncoder

from rashdf import RasPlanHdf

from pathlib import Path
from typing import List
from json import dumps


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


@register_check(["ble"], dependencies=["PlanHdfExists"])
class NoteEquationSet2D(RasqcChecker):
    """Checker for 2D equation set settings.

    Reports the selected 2D equation set for the current geometry of a RAS
    model as a 'note' to be reviewed by the user.
    """

    name = "2D Equation Set"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Check the 2D equation set used for a given RAS plan.

        Parameters
        ----------
            plan_hdf: The HEC-RAS plan HDF file to check.

            plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        if not plan_hdf:
            return RasqcResult(
                name=self.name,
                filename=plan_hdf_filename,
                result=ResultStatus.NOTE,
                message="Plan HDF file not found.",
            )
        else:
            plan_params = plan_hdf.get_plan_param_attrs()
            msg = dumps(
                {
                    n: e
                    for n, e in zip(
                        plan_params.get("2D Names"), plan_params.get("2D Equation Set")
                    )
                }
                if not isinstance(plan_params.get("2D Names"), (str, int, float))
                else plan_params.get("2D Equation Set"),
                cls=RasqcResultEncoder,
            )
        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the 2D equation set used for all RAS plan HDF files in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        return list(
            self._check(plan_file.hdf, Path(plan_file.hdf_path).name)
            for plan_file in ras_model.plans
        )


@register_check(["ble"], dependencies=["PlanHdfExists"])
class NoteCompSettings(RasqcChecker):
    """Checker for computational timestep settings.

    Reports the computational timestep settings for each plan of a RAS model
    as a 'note' to be reviewed by the user.
    """

    name = "Computation Settings"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Check the computational timestep settings used for a given RAS plan.

        Parameters
        ----------
            plan_hdf: The HEC-RAS plan HDF file to check.

            plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
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

        if not plan_hdf:
            return RasqcResult(
                name=self.name,
                filename=plan_hdf_filename,
                result=ResultStatus.NOTE,
                message="Plan HDF file not found.",
            )
        else:
            plan_info = plan_hdf.get_plan_info_attrs()
            msg = dumps(
                {
                    setting.lower(): plan_info[setting]
                    for setting in settings
                    if setting in plan_info
                },
                cls=RasqcResultEncoder,
            )
        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the comp settings used for all RAS plans in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        return list(
            self._check(plan_file.hdf, Path(plan_file.hdf_path).name)
            for plan_file in ras_model.plans
        )
