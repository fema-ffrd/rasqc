from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from json import dumps


@register_check(["ble"])
class FileStructure(RasqcChecker):
    name = "File Structure"

    def run(self, ras_model: RasModel) -> RasqcResult:
        msg_dict = {
            "title": ras_model.prj_file.title,
            "plans": {},
        }
        for plan in ras_model.plans:
            geom = ras_model.geom_files[plan.geom_file_ext]
            flow = ras_model.unsteady_flow_files[plan.flow_file_ext]
            msg_dict["plans"][plan.path.name] = {
                "title": plan.title,
                "geometry": {geom.filename: {"title": geom.title}},
                "unsteady": {flow.filename: {"title": flow.title}},
            }
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict),
        )
