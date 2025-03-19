from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf


@register_check(["ble"])
class OverflowMethod(RasqcChecker):
    name = "Structure Overflow Method"

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
            structs = geom_hdf.structures()
            flags = (
                structs.loc[
                    (structs["Use 2D for Overflow"] == 0)
                    & (structs["Mode"] == "Weir/Gate/Culverts")
                ]["Connection"]
                if not structs.empty
                else structs
            )
        if flags.empty:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.OK,
                message="any applicable structures found use 2d for overflow comps",
            )
        return RasqcResult(
            name=self.name,
            filename=filename,
            result=ResultStatus.WARNING,
            message={
                "message": f"{flags.shape[0]} applicable structures found not using 2d for overflow comps",
                "structure names": flags.to_list(),
            },
        )
