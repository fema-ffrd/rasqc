"""Checks related to the data layers associated with a HEC-RAS model."""

from rasqc.base_checker import RasqcChecker
from rasqc.registry import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf

from typing import List
from pathlib import Path


@register_check(["ble", "mesh"], dependencies=["GeomHdfExists"])
class MultiFaceManningN(RasqcChecker):
    """Checker for multiple face Manning's n values.

    Reports if the multiple face Manning's n option is checked
    in each 2D flow area.
    """

    name = "Multiple Face Manning's n"

    def _check(self, geom_hdf: RasGeomHdf, geom_hdf_filename: str) -> RasqcResult:
        """Execute multiple face Manning's n check for a RAS geometry HDF file.

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
                result=ResultStatus.WARNING,
                message="Geometry HDF file not found.",
            )
        try:
            area_attributes = geom_hdf.get_geom_2d_flow_area_attrs()
        except:
            return RasqcResult(
                name=self.name,
                filename=geom_hdf_filename,
                result=ResultStatus.WARNING,
                message="Error retrieving 2D flow area attributes from geometry HDF. Be sure to run Geometry Preprocessor.",
            )

        if area_attributes.get("Multiple Face Mann n") == 1:
            return RasqcResult(
                name=self.name,
                filename=geom_hdf_filename,
                result=ResultStatus.NOTE,
                message="Multiple Face Mann n is enabled in the geometry.",
            )
        return RasqcResult(
            name=self.name,
            filename=geom_hdf_filename,
            result=ResultStatus.NOTE,
            message="WARNING:Multiple Face Mann n is NOT enabled in the geometry.",
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check multiple face Manning's n for all RAS geom HDF files in a model.

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
