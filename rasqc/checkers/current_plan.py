from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus


@register_check(["ble"])
class CurrentPlan(RasqcChecker):
    def run(self, ras_model: RasModel) -> RasqcResult:
        return RasqcResult(
            name="Current Saved Plan",
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message={
                "File": ras_model.current_plan.path.name,
                "Title": ras_model.current_plan.title,
            },
        )
