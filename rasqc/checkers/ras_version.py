from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf


@register_check(["ble"])
class RasVersion(RasqcChecker):
    name = "HEC-RAS Version"

    def run(self, ras_model: RasModel) -> RasqcResult:
        filenames = []
        messages = []
        for geom_hdf_path in ras_model.geometry_hdf_paths:
            filenames.append(geom_hdf_path.name)
            if not geom_hdf_path.exists():
                messages.append(f"{geom_hdf_path.name} does not exist within the specified directory")
            else:
                geom_hdf = RasGeomHdf(geom_hdf_path)
                messages.append(geom_hdf.get_root_attrs()["File Version"])
        return RasqcResult(
            name=self.name,
            filename=filenames,
            result=ResultStatus.NOTE,
            message=messages,
        )
