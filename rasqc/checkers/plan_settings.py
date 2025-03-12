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
        equation_sets = (
            [plan_params["2D Equation Set"]]
            if isinstance(plan_params["2D Equation Set"], str)
            else plan_params["2D Equation Set"]
        )  # handle geometries with single or multiple 2D areas
        for equation_set in equation_sets:
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


@register_check(["ble"])
class EquationSet2DNote(RasqcChecker):
    name = "2D Equation Set"

    def run(self, ras_model: RasModel) -> RasqcResult:
        filenames = []
        messages = []
        for plan_hdf_path in ras_model.plan_hdf_paths:
            if plan_hdf_path.exists():
                filenames.append(plan_hdf_path.name)
                plan_hdf = RasPlanHdf(plan_hdf_path)
                plan_params = plan_hdf.get_plan_param_attrs()
                messages.append(
                    {
                        n: e
                        for n, e in zip(
                            plan_params["2D Names"], plan_params["2D Equation Set"]
                        )
                    }
                    if not isinstance(plan_params["2D Names"], (str, int, float))
                    else plan_params["2D Equation Set"]
                )
        return RasqcResult(
            name=self.name,
            filename=filenames,
            result=ResultStatus.NOTE,
            message=messages,
        )


@register_check(["ble"])
class CompSettings(RasqcChecker):
    name = "Computation Settings"

    def run(self, ras_model: RasModel) -> RasqcResult:
        settings = [
            "Computation Time Step Base",
            "Computation Time Courant Method",
            "Computation Time Step Max Courant",
            "Computation Time Step Min Courant",
            "Computation Time Step Count To Double",
            "Computation Time Step Max Doubling",
            "Computation Time Step Max Halving",
            "Time Window",
        ]
        filenames = []
        messages = []
        for plan_hdf_path in ras_model.plan_hdf_paths:
            if plan_hdf_path.exists():
                filenames.append(plan_hdf_path.name)
                plan_hdf = RasPlanHdf(plan_hdf_path)
                plan_info = plan_hdf.get_plan_info_attrs()
                messages.append(
                    {
                        setting.lower(): plan_info[setting]
                        for setting in settings
                        if setting in plan_info
                    }
                )
        return RasqcResult(
            name=self.name,
            filename=filenames,
            result=ResultStatus.NOTE,
            message=messages,
        )
