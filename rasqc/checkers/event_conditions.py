"""Checks related to the event conditions a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from json import dumps


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
            message=dumps(msg_dict),
        )
