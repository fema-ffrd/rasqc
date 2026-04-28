"""Checker for unit system settings."""

from rasqc.base_checker import RasqcChecker
from rasqc.registry import register_check
from rasqc.result import RasqcResult, ResultStatus, RasqcResultEncoder
from rasqc.rasmodel import RasModel
from rasqc import utils

from rashdf import RasPlanHdf

from typing import List
from pathlib import Path


@register_check(["ble"], dependencies=["PlanHdfExists"])
class NoteUnitSystem(RasqcChecker):
    """Checker for noting the unit system setting in the model."""

    name = "Unit System"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Check the unit system setting in the model.

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
                result=ResultStatus.WARNING,
                message="Plan HDF file not found.",
            )

        units = utils.get_units_system(plan_hdf)

        if not units:
            return RasqcResult(
                name=self.name,
                filename=plan_hdf_filename,
                result=ResultStatus.WARNING,
                message="Unit System not found.",
            )

        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=units,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the unit system for all plans in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        results = []
        for plan_file in ras_model.plans:
            plan_hdf = plan_file.hdf
            results.append(self._check(plan_hdf, Path(plan_file.hdf_path).name))
        return results
