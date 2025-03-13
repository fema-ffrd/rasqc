from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf


@register_check(["ble"])
class ErroneousCells(RasqcChecker):
    name = "Erroneous Cells"

    def run(self, ras_model: RasModel) -> RasqcResult:
        geom_hdf_path = ras_model.current_geometry.hdf_path
        filename = geom_hdf_path.name
        if not geom_hdf_path.exists():
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.WARNING,
                message=f"{filename} does not exist within the specified directory",
            )
        with RasGeomHdf(geom_hdf_path) as geom_hdf:
            cells = geom_hdf.mesh_cell_polygons()
            pnts = geom_hdf.mesh_cell_points()
            joined = cells.sjoin(pnts, how="left", predicate="intersects")
            flags = joined.loc[joined["index_right"].isna()].copy()
            flags.geometry = flags.geometry.apply(lambda g: g.exterior)
        if flags.empty:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.OK,
                message="no erroneous cells found",
            )
        return RasqcResult(
            name=self.name,
            filename=filename,
            result=ResultStatus.ERROR,
            message=f"{flags.shape[0]} erroneous cells found",
            gdf=flags,
        )
