"""Checks related to refinement regions within a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf
from pathlib import Path

ENFORCEMENT_TOLERANCE = 5
MIN_FLAG_LENGTH = 10


@register_check(["ble"], dependencies=["GeomHdfExists"])
class RefRegionEnforcement(RasqcChecker):
    """Checker for refinement region enforcement.

    Checks the refinement region enforcement within the current geometry and returns a `GeoDataFrame` of delinquent refinement regions.
    """

    name = "Refinement Region Enforcement"

    def _check(self, geom_hdf: RasGeomHdf, geom_hdf_filename: str) -> RasqcResult:
        """Execute refinement region enforcement check for a RAS geometry HDF file.

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
        rrs = geom_hdf.refinement_regions()
        if rrs.empty:
            return RasqcResult(
                name=self.name,
                filename=geom_hdf_filename,
                result=ResultStatus.WARNING,
                message="no refinement regions found within the model geometry",
            )
        rrs.geometry = rrs.geometry.apply(lambda g: g.exterior)
        flags_all = rrs.overlay(
            mesh_faces.buffer(ENFORCEMENT_TOLERANCE).to_frame(),
            how="difference",
            keep_geom_type=True,
        ).explode()
        flags_filtered = flags_all[flags_all["geometry"].length >= MIN_FLAG_LENGTH]
        if flags_filtered.empty:
            return RasqcResult(
                name=self.name,
                filename=geom_hdf_filename,
                result=ResultStatus.OK,
                message="no refinement region enforcement flags found",
            )
        return RasqcResult(
            name=self.name,
            filename=geom_hdf_filename,
            result=ResultStatus.WARNING,
            message=f"{flags_filtered.shape[0]} refinement region enforcement flags found",
            gdf=flags_filtered,
        )

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute refinement region enforcement check for a HEC-RAS model.

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
