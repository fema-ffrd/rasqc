from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

import re


@register_check(["ffrd"])
class PrjNaming(RasqcChecker):
    name = "Project file naming"

    def run(self, ras_model: RasModel) -> RasqcResult:
        filename = ras_model.prj_file.name
        if not re.match(r"\w*\d{4}\w*\.prj", filename):
            return RasqcResult(
                name=self.name,
                result=ResultStatus.ERROR,
                message=f"HEC-RAS project file '{filename}' does not follow the naming convention 'Basin_Name_<HUC4-ID>_Subbasin_name.prj' where <HUC4-ID> is a 4-digit HUC number.",
            )
        return RasqcResult(name=self.name, result=ResultStatus.OK)
        