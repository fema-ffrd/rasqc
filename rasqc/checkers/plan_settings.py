from rasqc.checkers.base_checker import RasqcChecker
from rasqc.checksuite import register_check
from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rashdf import RasPlanHdf


@register_check(["ffrd"])
class EquationSet2D(RasqcChecker):
    name = "2D Equation Set"

    def run(self, ras_model: RasModel) -> RasqcResult:
        plan_hdf_path = ras_model.current_plan.hdf_path
        filename = plan_hdf_path.name
        plan_hdf = RasPlanHdf(plan_hdf_path)
        plan_params = plan_hdf.get_plan_param_attrs()
        equation_set = (
            plan_params["2D Equation Set"]
            if isinstance(plan_params["2D Equation Set"], str)
            else plan_params["2D Equation Set"][0]
        )  # handle geometries with single or multiple 2D areas
        if equation_set != "Diffusion Wave":
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.WARNING,
                message=(
                    f"2D Equation Set '{equation_set}'"
                    " does not match expected setting: 'Diffusion Wave'."
                    f" ({filename})"
                ),
            )
        return RasqcResult(name=self.name, result=ResultStatus.OK, filename=filename)
