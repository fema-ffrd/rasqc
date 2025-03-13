from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf


@register_check(["ble"])
class ShortCellFaces(RasqcChecker):
    name = "Short Cell Faces"

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
            mesh_faces = geom_hdf.mesh_cell_faces()
            flags = mesh_faces.loc[mesh_faces["geometry"].length < 10].copy()
        if flags.empty:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.OK,
                message="no short cell faces found",
            )
        return RasqcResult(
            name=self.name,
            filename=filename,
            result=ResultStatus.WARNING,
            message=f"{flags.shape[0]} short cell faces found",
            gdf=flags,
        )
