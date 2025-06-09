"""Checks related to the event conditions a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus, RasqcResultEncoder

from json import dumps

BC_PATH = "/Event Conditions/Unsteady/Boundary Conditions"
IC_PATH = "/Event Conditions/Unsteady/Initial Conditions"


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
        attrs = ["2D Flow Area"]
        for plan in ras_model.plan_files.values():
            plan_key = plan.path.suffix.strip(".") + f" ({plan.title})"
            if plan.hdf:
                if precip_hydrographs_path in plan.hdf:
                    for p in plan.hdf[precip_hydrographs_path].values():
                        msg_dict.setdefault(plan_key, []).append(
                            {k: v for k, v in p.attrs.items() if k in attrs}
                            | {"Depth": round(float(p[:, 1].sum()), 3)}
                        )
                else:
                    msg_dict[plan_key] = "No precip hydrograph applied."
            else:
                msg_dict[plan_key] = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict, cls=RasqcResultEncoder),
        )


@register_check(["ble"])
class FlowHydrographs(RasqcChecker):
    """Flow hydrographs check.

    Reports the boundary condition flow hydrographs applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Flow Hydrographs"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute flow hydrographs check of the HEC-RAS model.

        Parameters
        ----------
            ras_model: RasModel
                The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        flow_hydrographs_path = BC_PATH + "/Flow Hydrographs"
        msg_dict = {}
        attrs = ["2D Flow Area", "BC Line", "EG Slope For Distributing Flow"]
        for plan in ras_model.plan_files.values():
            plan_key = plan.path.suffix.strip(".") + f" ({plan.title})"
            if plan.hdf:
                if flow_hydrographs_path in plan.hdf:
                    for p in plan.hdf[flow_hydrographs_path].values():
                        msg_dict.setdefault(plan_key, []).append(
                            {k: v for k, v in p.attrs.items() if k in attrs}
                            | {"Peak Flow": round(float(p[:, 1].max()), 3)}
                        )
                else:
                    msg_dict[plan_key] = "No flow hydrograph applied."
            else:
                msg_dict[plan_key] = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict, cls=RasqcResultEncoder),
        )


@register_check(["ble"])
class StageHydrographs(RasqcChecker):
    """Stage hydrographs check.

    Reports the boundary condition stage hydrographs applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Stage Hydrographs"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute stage hydrographs check of the HEC-RAS model.

        Parameters
        ----------
            ras_model: RasModel
                The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        stage_hydrographs_path = BC_PATH + "/Stage Hydrographs"
        msg_dict = {}
        attrs = ["2D Flow Area", "BC Line", "Use Initial Stage"]
        for plan in ras_model.plan_files.values():
            plan_key = plan.path.suffix.strip(".") + f" ({plan.title})"
            if plan.hdf:
                if stage_hydrographs_path in plan.hdf:
                    for p in plan.hdf[stage_hydrographs_path].values():
                        msg_dict.setdefault(plan_key, []).append(
                            {k: v for k, v in p.attrs.items() if k in attrs}
                            | {"Peak Stage": round(float(p[:, 1].max()), 3)}
                        )
                else:
                    msg_dict[plan_key] = "No stage hydrograph applied."
            else:
                msg_dict[plan_key] = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict, cls=RasqcResultEncoder),
        )


@register_check(["ble"])
class NormalDepths(RasqcChecker):
    """Normal depths check.

    Reports the boundary condition normal depths applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Normal Depths"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute normal depths check of the HEC-RAS model.

        Parameters
        ----------
            ras_model: RasModel
                The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        normal_depths_path = BC_PATH + "/Normal Depths"
        msg_dict = {}
        attrs = ["2D Flow Area", "BC Line", "BC Line WS"]
        for plan in ras_model.plan_files.values():
            plan_key = plan.path.suffix.strip(".") + f" ({plan.title})"
            if plan.hdf:
                if normal_depths_path in plan.hdf:
                    for p in plan.hdf[normal_depths_path].values():
                        msg_dict.setdefault(plan_key, []).append(
                            {k: v for k, v in p.attrs.items() if k in attrs}
                            | {"Normal Depth Slope": float(p[0])}
                        )
                else:
                    msg_dict[plan_key] = "No normal depth applied."
            else:
                msg_dict[plan_key] = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict, cls=RasqcResultEncoder),
        )


@register_check(["ble"])
class RatingCurves(RasqcChecker):
    """Rating curves check.

    Reports the boundary condition rating curves applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Rating Curves"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute rating curves check of the HEC-RAS model.

        Parameters
        ----------
            ras_model: RasModel
                The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        rating_curves_path = BC_PATH + "/Rating Curves"
        msg_dict = {}
        attrs = ["2D Flow Area", "BC Line"]
        for plan in ras_model.plan_files.values():
            plan_key = plan.path.suffix.strip(".") + f" ({plan.title})"
            if plan.hdf:
                if rating_curves_path in plan.hdf:
                    for p in plan.hdf[rating_curves_path].values():
                        msg_dict.setdefault(plan_key, []).append(
                            {k: v for k, v in p.attrs.items() if k in attrs}
                        )
                else:
                    msg_dict[plan_key] = "No rating curve applied."
            else:
                msg_dict[plan_key] = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict, cls=RasqcResultEncoder),
        )


@register_check(["ble"])
class InitialConditions(RasqcChecker):
    """Initial conditions check.

    Reports the initial conditions applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Initial Conditions"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Execute initial conditions check of the HEC-RAS model.

        Parameters
        ----------
            ras_model: RasModel
                The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        ic_name_path = IC_PATH + "/IC Point Names"
        ic_elev_path = IC_PATH + "/IC Point Elevations"
        msg_dict = {}
        for plan in ras_model.plan_files.values():
            plan_key = plan.path.suffix.strip(".") + f" ({plan.title})"
            if plan.hdf:
                if ic_name_path in plan.hdf:
                    msg_dict[plan_key] = {
                        k.decode(): round(v, 3)
                        for k, v in zip(plan.hdf[ic_name_path], plan.hdf[ic_elev_path])
                    }
                else:
                    msg_dict[plan_key] = "No initial conditions applied."
            else:
                msg_dict[plan_key] = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.NOTE,
            message=dumps(msg_dict, cls=RasqcResultEncoder),
        )
