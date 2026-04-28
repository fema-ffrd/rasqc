"""Checks related to erroneous 2D mesh cells within a HEC-RAS model."""

from rasqc.base_checker import RasqcChecker
from rasqc.registry import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus
from rasqc.utils import calculate_min_angle

from rashdf import RasGeomHdf
from pathlib import Path

MIN_ANGLE = 75


@register_check(["mesh"], dependencies=["GeomHdfExists"])
class ErroneousFaces(RasqcChecker):
    """Checker for erroneous 2D mesh faces.

    Checks the current geometry within a RAS model and returns a `GeoDataFrame`
    of erroneous 2D mesh faces (those with an interior angle of less than 75 degrees).
    """

    name = "Erroneous Faces"

    def _check(self, geom_hdf: RasGeomHdf, geom_hdf_filename: str) -> RasqcResult:
        """Execute erroneous face check for a RAS geometry HDF file.

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

        # Calculate minimum angle for each face
        mesh_faces["min_angle"] = mesh_faces["geometry"].apply(calculate_min_angle)

        # Filter faces with angle less than MIN_ANGLE
        face_flags = mesh_faces.loc[mesh_faces["min_angle"] < MIN_ANGLE].copy()

        if face_flags.empty:
            return RasqcResult(
                name=self.name,
                filename=geom_hdf_filename,
                result=ResultStatus.OK,
                message="no erroneous faces found",
            )
        return RasqcResult(
            name=self.name,
            filename=geom_hdf_filename,
            result=ResultStatus.ERROR,
            message=f"{face_flags.shape[0]} erroneous faces found",
            gdf=face_flags,
        )

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute erroneous face check for a HEC-RAS model.

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
