from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf


@register_check(["ble"])
class RasVersion(RasqcChecker):
    name = "HEC-RAS Version"

    def run(self, ras_model: RasModel) -> RasqcResult:
        geom_hdf_path = ras_model.current_geometry.hdf_path
        geom_hdf = RasGeomHdf(geom_hdf_path)
        ras_version = geom_hdf.attrs.get("File Version").decode()
        filename = geom_hdf_path.name
        return RasqcResult(
            name=self.name,
            filename=filename,
            result=ResultStatus.NOTE,
            message=(f"HEC-RAS geometry version: '{ras_version}'"),
        )
