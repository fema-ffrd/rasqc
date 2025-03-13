from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf


@register_check(["ble"])
class BreaklineEnforcement(RasqcChecker):
    name = "Breakline Enforcement"

    def run(self, ras_model: RasModel) -> RasqcResult:
        geom_hdf_path = ras_model.current_geometry.hdf_path
        filename = geom_hdf_path.name
        with RasGeomHdf(geom_hdf_path) as geom_hdf:
            mesh_faces = geom_hdf.mesh_cell_faces()
            bls = geom_hdf.breaklines()
            if bls.empty:
                return RasqcResult(
                    name=self.name,
                    filename=filename,
                    result=ResultStatus.WARNING,
                    message="no breaklines found within the model geometry",
                )
            flags_all = bls.overlay(
                mesh_faces.buffer(5).to_frame(), how="difference", keep_geom_type=True
            ).explode()
            flags_filtered = flags_all.loc[flags_all["geometry"].length >= 10].copy()
        if flags_filtered.empty:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.OK,
                message="no breakline enforcement flags found",
            )
        return RasqcResult(
            name=self.name,
            filename=filename,
            result=ResultStatus.WARNING,
            message=f"{flags_filtered.shape[0]} breakline enforcement flags found",
            gdf=flags_filtered,
        )
