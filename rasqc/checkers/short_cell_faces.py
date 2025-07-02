"""Checks related to 2D mesh cell face length."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf
from pathlib import Path

MIN_FACE_LENGTH_FEET = 10


@register_check(["ble"], dependencies=["GeomHdfExists"])
class ShortCellFaces(RasqcChecker):
    """Checker for short 2D mesh cell faces.

    Checks the current geometry within a RAS model for short
    cell faces that can be a source of instabilities.
    Any polyline features with a lenth < `MIN_FACE_LENGTH_FEET`
    are returned as a `GeoDataFrame` within the `RasqcResult`
    object.
    """

    name = "Short Cell Faces"

    def _check(self, geom_hdf: RasGeomHdf, geom_hdf_filename: str) -> RasqcResult:
        """Execute short 2D mesh cell faces check for a RAS geometry HDF file.

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
        mesh_faces = geom_hdf.mesh_cell_faces()
        flags = mesh_faces.loc[
            mesh_faces["geometry"].length < MIN_FACE_LENGTH_FEET
        ].copy()
        if flags.empty:
            return RasqcResult(
                name=self.name,
                filename=geom_hdf_filename,
                result=ResultStatus.OK,
                message="no short cell faces found",
            )
        return RasqcResult(
            name=self.name,
            filename=geom_hdf_filename,
            result=ResultStatus.ERROR,
            message=f"{flags.shape[0]} short cell faces found",
            gdf=flags,
        )

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute short 2D mesh cell faces check for a HEC-RAS model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return self._check(
            ras_model.current_geometry.hdf,
            Path(ras_model.current_geometry.hdf_path).name,
        )
