from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from pyproj import CRS
from rashdf import RasGeomHdf


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
FFRD_CRS = CRS.from_wkt(FFRD_PROJECTION_WKT)


@register_check(["ffrd"])
class GeomProjection(RasqcChecker):
    name = "Geometry Projection"

    def run(self, ras_model: RasModel) -> RasqcResult:
        geom_hdf_path = ras_model.current_geometry.hdf_path
        geom_hdf = RasGeomHdf(geom_hdf_path)
        projection = geom_hdf.projection()
        filename = geom_hdf_path.name
        if not projection:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.WARNING,
                message="HEC-RAS geometry HDF file does not have a projection defined.",
            )
        if projection != FFRD_CRS:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS geometry HDF file projection '{projection.name}'"
                    " does not match the expected projection for FFRD models."
                    f" ({filename})"
                ),
            )
        return RasqcResult(name=self.name, result=ResultStatus.OK, filename=filename)


@register_check(["ble"])
class GeomProjectionNote(RasqcChecker):
    name = "Geometry Projection"

    def run(self, ras_model: RasModel) -> RasqcResult:
        geom_hdf_path = ras_model.current_geometry.hdf_path
        geom_hdf = RasGeomHdf(geom_hdf_path)
        projection = geom_hdf.projection()
        filename = geom_hdf_path.name
        if not projection:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.ERROR,
                message="HEC-RAS geometry HDF file does not have a projection defined.",
            )
        return RasqcResult(
            name=self.name,
            filename=filename,
            result=ResultStatus.NOTE,
            message=projection.name,
        )
