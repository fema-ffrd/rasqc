"""Checks related to the data layers associated with a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus, RasqcResultEncoder

from rashdf import RasGeomHdf

from json import dumps
from typing import List
from pathlib import Path


@register_check(["ble"], dependencies=["GeomHdfExists"])
class AssociatedLayers(RasqcChecker):
    """Checker for associated model layers.

    Reports the layers (e.g., terrain, land cover, etc.) associated with each geometry as a 'note' to be reviewed by the user.
    """

    name = "Associated Layers"

    def _check(self, geom_hdf: RasGeomHdf, geom_hdf_filename: str) -> RasqcResult:
        """Execute associated layers check for a RAS geometry HDF file.

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
        else:
            geom_attrs = geom_hdf.get_geom_attrs()
            msg = dumps(
                {
                    "terrain": geom_attrs["Terrain Filename"]
                    if "Terrain Filename" in geom_attrs
                    else None,
                    "land cover": geom_attrs["Land Cover Filename"]
                    if "Land Cover Filename" in geom_attrs
                    else None,
                    "infiltration": geom_attrs["Infiltration Filename"]
                    if "Infiltration Filename" in geom_attrs
                    else None,
                },
                cls=RasqcResultEncoder,
            )
        return RasqcResult(
            name=self.name,
            filename=geom_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the associated layers for all RAS geom HDF files in a model.

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
