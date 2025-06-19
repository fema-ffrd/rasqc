"""Checks related to erroneous 2D mesh cells within a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf
from pathlib import Path


@register_check(["ble"], dependencies=["GeomHdfExists"])
class ErroneousCells(RasqcChecker):
    """Checker for erroneous 2D mesh cells.

    Checks the current geometry within a RAS model and returns a `GeoDataFrame` of erroneous 2D mesh cells (those with the center point outside the cell boundary).
    """

    name = "Erroneous Cells"

    def _check(self, geom_hdf: RasGeomHdf, geom_hdf_filename: str) -> RasqcResult:
        """Execute erroneous cell check for a RAS geometry HDF file.

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
        cells = geom_hdf.mesh_cell_polygons()
        pnts = geom_hdf.mesh_cell_points()
        joined = cells.sjoin(pnts, how="left", predicate="intersects")
        flags = joined.loc[joined["index_right"].isna()].copy()
        flags.geometry = flags.geometry.apply(lambda g: g.exterior)
        if flags.empty:
            return RasqcResult(
                name=self.name,
                filename=geom_hdf_filename,
                result=ResultStatus.OK,
                message="no erroneous cells found",
            )
        return RasqcResult(
            name=self.name,
            filename=geom_hdf_filename,
            result=ResultStatus.ERROR,
            message=f"{flags.shape[0]} erroneous cells found",
            gdf=flags,
        )

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute erroneous cell check for a HEC-RAS model.

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
