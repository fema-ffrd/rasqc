"""Checker for FFRD geometry projection settings."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from pyproj import CRS
from rashdf import RasGeomHdf

from pathlib import Path
from typing import List


# Well-known text representation of the FFRD projection
FFRD_PROJECTION_WKT = """
PROJCS["USA_Contiguous_Albers_Equal_Area_Conic_USGS_version",
    GEOGCS["GCS_North_American_1983",
        DATUM["D_North_American_1983",
            SPHEROID["GRS_1980",6378137.0,298.257222101]],
        PRIMEM["Greenwich",0.0],
        UNIT["Degree",0.0174532925199433]],
    PROJECTION["Albers"],
    PARAMETER["False_Easting",0.0],
    PARAMETER["False_Northing",0.0],
    PARAMETER["Central_Meridian",-96.0],
    PARAMETER["Standard_Parallel_1",29.5],
    PARAMETER["Standard_Parallel_2",45.5],
    PARAMETER["Latitude_Of_Origin",23.0],
    UNIT["Foot_US",0.3048006096012192]]'
"""
# Create a CRS object from the WKT
FFRD_CRS = CRS.from_wkt(FFRD_PROJECTION_WKT)


@register_check(["ffrd"], dependencies=["GeomHdfExists"])
class GeomProjection(RasqcChecker):
    """Checker for geometry projection settings.

    Checks if the geometry projection matches the expected projection
    for FFRD models (USA Contiguous Albers Equal Area Conic USGS version).
    """

    name = "Geometry Projection"

    def _check(self, geom_hdf: RasGeomHdf, ghdf_filename: str) -> RasqcResult:
        """Check if the geometry projection matches the expected projection.

        Parameters
        ----------
            geom_hdf: The HEC-RAS geometry HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        projection = geom_hdf.projection()
        if not projection:
            return RasqcResult(
                name=self.name,
                filename=ghdf_filename,
                result=ResultStatus.WARNING,
                message="HEC-RAS geometry HDF file does not have a projection defined.",
            )
        if projection != FFRD_CRS:
            return RasqcResult(
                name=self.name,
                filename=ghdf_filename,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS geometry HDF file projection '{projection.name}'"
                    " does not match the expected projection for FFRD models."
                ),
            )
        return RasqcResult(
            name=self.name, result=ResultStatus.OK, filename=ghdf_filename
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the geometry projection matches the expected projection.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        results = []
        for geom_file in ras_model.geometries:
            ghdf = geom_file.hdf
            if ghdf:
                results.append(self._check(ghdf, Path(geom_file.hdf_path).name))
        return results
