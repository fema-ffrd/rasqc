"""Module for simulation max velocity check."""

from sys import flags
from rasqc.base_checker import RasqcChecker
from rasqc.registry import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus
from rasqc import utils as util

from rashdf import RasPlanHdf, utils

from pathlib import Path
from typing import List

MAX_VEL_FLAG = 15


@register_check(["ble", "stability"], dependencies=["PlanHdfExists"])
class MaxVelocity(RasqcChecker):
    """Checker for high maximum velocity in mesh faces.

    Checks if the maximum velocity exceeds the defined threshold of MAX_VEL_FLAG
    in feet per second. If the unit sistem is SI, the threshold is converted to
    meters per second.
    """

    name = "Maximum Velocity"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Check the maximum velocity in mesh faces for a RAS plan HDF file.

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
        mesh_faces = plan_hdf.mesh_cell_faces()

        if util.get_units_system(plan_hdf) == "SI Units":
            max_vel_threshold = round(MAX_VEL_FLAG * 0.3048, 1)  # Convert feet/s to m/s
            units = "m/s"
        else:
            max_vel_threshold = MAX_VEL_FLAG
            units = "ft/s"
        vel_flags = mesh_faces.loc[mesh_faces["max_v"] >= max_vel_threshold].copy()

        flags_st = utils.df_datetimes_to_str(vel_flags)

        if not vel_flags.empty:
            return RasqcResult(
                name=self.name,
                filename=plan_hdf_filename,
                result=ResultStatus.ERROR,
                message=f"{vel_flags.shape[0]} faces have maximum velocity greater than or equal to {max_vel_threshold} {units}.",
                gdf=flags_st,
            )
        return RasqcResult(
            name=self.name,
            result=ResultStatus.OK,
            filename=plan_hdf_filename,
            message=f"All faces have maximum velocity less than {max_vel_threshold} {units}.",
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the maximum face velocity for all RAS plan HDF files in a model.

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
