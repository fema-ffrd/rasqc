"""Checks related to the HEC-RAS version used to develop a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf

from typing import List
from pathlib import Path


@register_check(["ble"], dependencies=["GeomHdfExists"])
class RasVersion(RasqcChecker):
    """Checker for the HEC-RAS version used.

    Reports the RAS version used to develop a RAS model as a 'note' to be
    reviewed by the user.
    """

    name = "HEC-RAS Version"

    def _check(self, geom_hdf: RasGeomHdf, geom_hdf_filename: str) -> RasqcResult:
        """Check the HEC-RAS version used to develop a HEC-RAS model geometry.

        Parameters
        ----------
            geom_hdf: The HEC-RAS geometry HDF file to check.

            geom_hdf_filename: The file name of the HEC-RAS geometry HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        if not geom_hdf:
            return RasqcResult(
                name=self.name,
                filename=geom_hdf_filename,
                result=ResultStatus.NOTE,
                message="Geometry HDF file not found.",
            )
        return RasqcResult(
            name=self.name,
            filename=geom_hdf_filename,
            result=ResultStatus.NOTE,
            message=geom_hdf.get_root_attrs()["File Version"],
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Execute the check for each geometry within a HEC-RAS model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        return list(
            self._check(geom_file.hdf, Path(geom_file.hdf_path).name)
            for geom_file in ras_model.geometries
        )
