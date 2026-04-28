"""Module for simulation computational iterations check."""

from sys import flags
from rasqc.base_checker import RasqcChecker
from rasqc.registry import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasPlanHdf, utils

from pathlib import Path
from typing import List

ITER_FLAG = 1
LAST_FLAG = 10


@register_check(["ble", "stability"], dependencies=["PlanHdfExists"])
class Iterations(RasqcChecker):
    """Checker for computational iterations.

    Checks the number of computational iterations that occur in each mesh cell and flags
    cells with more iterations than the threshold set by ITER_FLAG. Also flags cells that
    show they are the last cell iterating in a time step in more time steps than the LAST_FLAG
    to show the cells that are causing long run times.
    """

    name = "Iterations"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Check the number of computational iterations in mesh cells for a RAS plan HDF file.

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

        iter_flags = mesh_cells.loc[
            (mesh_cells["max_iter"] > ITER_FLAG) | (mesh_cells["last_iter"] > LAST_FLAG)
        ].copy()

        flags_st = utils.df_datetimes_to_str(iter_flags)

        if not iter_flags.empty:
            return RasqcResult(
                name=self.name,
                filename=plan_hdf_filename,
                result=ResultStatus.ERROR,
                message=f"{iter_flags.shape[0]} cells have iteration counts exceeding limits.",
                gdf=flags_st,
            )
        return RasqcResult(
            name=self.name,
            result=ResultStatus.OK,
            filename=plan_hdf_filename,
            message=f"All cells have iteration counts within limits.",
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the number of computational iterations for all RAS plan HDF files in a model.

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
