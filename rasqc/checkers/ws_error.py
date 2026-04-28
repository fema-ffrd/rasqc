"""Module for simulation computational water surface error check."""

from sys import flags
from rasqc.base_checker import RasqcChecker
from rasqc.registry import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasPlanHdf, utils

from pathlib import Path
from typing import List

ERROR_FLAG = 0.01


@register_check(["ble", "stability"], dependencies=["PlanHdfExists"])
class WaterSurfaceError(RasqcChecker):
    """Checker for computational water surface errors.

    Checks the maximum water surface error that occurs in each mesh cell.
    """

    name = "Water Surface Error"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Check the maximum water surface error in mesh cells for a RAS plan HDF file.

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
        mesh_cells = plan_hdf.mesh_cell_polygons()

        error_flags = mesh_cells.loc[(mesh_cells["max_ws_err"] > ERROR_FLAG)].copy()

        flags_st = utils.df_datetimes_to_str(error_flags)

        if not error_flags.empty:
            return RasqcResult(
                name=self.name,
                filename=plan_hdf_filename,
                result=ResultStatus.ERROR,
                message=f"{error_flags.shape[0]} cells have water surface errors exceeding {ERROR_FLAG}.",
                gdf=flags_st,
            )
        return RasqcResult(
            name=self.name,
            result=ResultStatus.OK,
            filename=plan_hdf_filename,
            message=f"All cells have water surface errors within limits.",
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the water surface errors for all RAS plan HDF files in a model.

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
