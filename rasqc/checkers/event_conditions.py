"""Checks related to the event conditions a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus, RasqcResultEncoder

from json import dumps

BC_PATH = "/Event Conditions/Unsteady/Boundary Conditions/"


@register_check(["ble"])
class MeteorologyPrecip(RasqcChecker):
    """Meterology precipitation check.

    Reports the meterological condition precipitation applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Meteorology Precipitation"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute meterology precipitation check of the HEC-RAS model.

        Parameters
        ----------
            ras_model: RasModel
                The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        msg_dict = {}
        attrs = ["DSS Filename", "DSS Pathname"]
        for plan in ras_model.plan_files.values():
            msg_dict[plan.path.suffix.strip(".") + f" ({plan.title})"] = (
                {
                    k: v
                    for k, v in plan.hdf.get_meteorology_precip_attrs().items()
                    if k in attrs
                }
                if plan.hdf
                else "No HDF file located."
            ) or "No meteorology precip applied."
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict, cls=RasqcResultEncoder),
        )


@register_check(["ble"])
class PrecipHydrographs(RasqcChecker):
    """Precipitation hydrographs check.

    Reports the boundary condition precipitation hydrographs applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Precipitation Hydrographs"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute precipitation hydrographs check of the HEC-RAS model.

        Parameters
        ----------
            ras_model: RasModel
                The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        precip_hydrographs_path = BC_PATH + "/Precipitation Hydrographs"
        msg_dict = {}
        attrs = ["2D Flow Area", "Start Date", "End Date"]
        for plan in ras_model.plan_files.values():
            if plan.hdf:
                if precip_hydrographs_path in plan.hdf:
                    for p in plan.hdf[precip_hydrographs_path].values():
                        msg_dict[plan.path.suffix.strip(".") + f" ({plan.title})"] = {
                            k: v for k, v in p.attrs.items() if k in attrs
                        } | dict(depth=round(float(p[:, 1].sum()), 3))
                else:
                    msg_dict[plan.path.suffix.strip(".") + f" ({plan.title})"] = (
                        "No precip hydrograph applied."
                    )
            else:
                msg_dict[plan.path.suffix.strip(".") + f" ({plan.title})"] = (
                    "No HDF file located."
                )
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict, cls=RasqcResultEncoder),
        )
