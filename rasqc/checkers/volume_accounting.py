"""Module for simulation volume accounting checks."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from rashdf import RasPlanHdf

from pathlib import Path
from typing import List

VOL_ERR_PER_TOL = 2


@register_check(["ble"], dependencies=["PlanHdfExists"])
class VolumeError(RasqcChecker):
    """Checker for volume accounting errors.

    Checks if the volume accounting error is less than 2% of the total volume.
    """

    name = "Volume Accounting Error"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Check the volume accounting error for a RAS plan HDF file.

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
        vol_err = plan_hdf.get_results_volume_accounting_attrs()["Error Percent"]
        if vol_err > VOL_ERR_PER_TOL:
            return RasqcResult(
                name=self.name,
                filename=plan_hdf_filename,
                result=ResultStatus.ERROR,
                message=(
                    f"Volume accounting error percent of '{vol_err}' is greater than"
                    f" the acceptable tolerance of {VOL_ERR_PER_TOL}."
                ),
            )
        return RasqcResult(
            name=self.name, result=ResultStatus.OK, filename=plan_hdf_filename
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the volume accounting error for all RAS plan HDF files in a model.

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
