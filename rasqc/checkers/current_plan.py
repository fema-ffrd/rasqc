from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus


@register_check(["ble"])
class CurrentPlan(RasqcChecker):
    name = "Current Saved Plan"

    def run(self, ras_model: RasModel) -> RasqcResult:
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message={
                "file": ras_model.current_plan.path.name,
                "title": ras_model.current_plan.title,
            },
        )
