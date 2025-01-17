from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

import re


@register_check(["ffrd", "asdf"])
class PrjFileNaming(RasqcChecker):
    name = "Project file naming"

    def run(self, ras_model: RasModel) -> RasqcResult:
        filename = ras_model.prj_file.path.name
        if not re.match(r"\w*_\d{4}_\w*\.prj", filename):
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS project file '{filename}' does not follow the"
                    " naming convention 'Basin_Name_<HUC4-ID>_Subbasin_name.prj',"
                    " where <HUC4-ID> is a 4-digit HUC number."
                ),
            )
        return RasqcResult(name=self.name, result=ResultStatus.OK)


@register_check(["ffrd"])
class GeometryTitleNaming(RasqcChecker):
    name = "Geometry title naming"

    def run(self, ras_model: RasModel) -> RasqcResult:
        geom_file = ras_model.current_geometry
        geom_title = geom_file.title
        if not re.match(r"\w* FFRD$", geom_title):
            return RasqcResult(
                name=self.name,
                filename=geom_file.path.name,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS geometry file title '{geom_title}' does not follow the"
                    f" naming convention 'Watershed Name FFRD' ({geom_file.path.name})"
                ),
            )
        return RasqcResult(name=self.name, result=ResultStatus.OK)


@register_check(["ffrd"])
class PlanTitleNaming(RasqcChecker):
    name = "Plan title naming"

    def run(self, ras_model: RasModel) -> RasqcResult:
        plan_file = ras_model.current_plan
        plan_title = plan_file.title
        match = re.match(r"(\w{3})(\d{4}) .*$", plan_title)
        if not match:
            return RasqcResult(
                name=self.name,
                filename=plan_file.path.name,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS plan file title '{plan_title}' does not follow the"
                    f" naming convention 'MonYEAR Event' ({plan_file.path.name})"
                ),
            )
        return RasqcResult(name=self.name, result=ResultStatus.OK)


@register_check(["ffrd"])
class UnsteadyFlowTitleNaming(RasqcChecker):
    name = "Unsteady flow title naming"

    def run(self, ras_model: RasModel) -> RasqcResult:
        flow_file = ras_model.current_unsteady
        flow_title = flow_file.title
        match = re.match(r"(\w{3})(\d{4})", flow_title)
        if not match:
            return RasqcResult(
                name=self.name,
                filename=flow_file.path.name,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS unsteady flow file title '{flow_title}' does not follow the"
                    f" naming convention 'MonYEAR' ({flow_file.path.name})"
                ),
            )
        return RasqcResult(name=self.name, result=ResultStatus.OK)
