from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus


@register_check(["ble"])
class FileStructure(RasqcChecker):
    def run(self, ras_model: RasModel) -> RasqcResult:
        msg_dict = {
            ras_model.prj_file.path.name: {
                "title": ras_model.prj_file.title,
                "plans": {},
            }
        }
        for plan in ras_model.plans:
            msg_dict[ras_model.prj_file.path.name]["plans"][plan.path.name] = {
                "title": plan.title,
                "geometry": {
                    plan.associated_geometry.path.name: plan.associated_geometry.title
                },
                "unsteady": {
                    plan.associated_unsteady.path.name: plan.associated_unsteady.title
                },
            }
        return RasqcResult(
            name="File Structure",
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=msg_dict,
        )
