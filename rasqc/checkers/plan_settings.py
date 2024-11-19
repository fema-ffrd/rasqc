from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasPlanHdf

@register_check(["ffrd"])
class EquationSet2D(RasqcChecker):
    name = "2D Equation Set"

    def run(self, ras_model: RasModel) -> RasqcResult:
        plan_path = ras_model.plan_file().path
        plan_hdf_path = plan_path.with_suffix(plan_path.suffix + ".hdf")
        filename = plan_hdf_path.name
        plan_hdf = RasPlanHdf(plan_hdf_path)
        plan_params = plan_hdf.get_plan_param_attrs()
        equation_set = plan_params["2D Equation Set"]
        if equation_set != "Diffusion Wave":
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.WARNING,
                message=(f"2D Equation Set '{equation_set}'"
                         " does not match expected setting: 'Diffusion Wave'."
                         f" ({filename})")
            )
        return RasqcResult(name=self.name, result=ResultStatus.OK, filename=filename)
