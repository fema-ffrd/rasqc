"""Checks related to the event conditions a HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel, RasPlanHdf
from ..result import RasqcResult, ResultStatus, RasqcResultEncoder

from json import dumps
from typing import List
from pathlib import Path

BC_PATH = "/Event Conditions/Unsteady/Boundary Conditions"
IC_PATH = "/Event Conditions/Unsteady/Initial Conditions"


@register_check(["ble"], dependencies=["PlanHdfExists"])
class MeteorologyPrecip(RasqcChecker):
    """Checker for meterology precipitation.

    Reports the meterological condition precipitation applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Meteorology Precipitation"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Execute meterology precipitation check for a RAS plan HDF file.

        Parameters
        ----------
            plan_hdf: The HEC-RAS plan HDF file to check.

            plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        attrs = ["DSS Filename", "DSS Pathname"]
        if plan_hdf:
            mp_attrs = plan_hdf.get_meteorology_precip_attrs()
            if mp_attrs:
                msg = dumps(
                    {k: v for k, v in mp_attrs.items() if k in attrs},
                    cls=RasqcResultEncoder,
                )
            else:
                msg = "No meteorology precip applied."
        else:
            msg = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the meterology precipitation for all RAS plan HDF files in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        results = []
        for plan_file in ras_model.plans:
            plan_hdf = plan_file.hdf
            results.append(self._check(plan_hdf, Path(plan_file.hdf_path).name))
        return results


@register_check(["ble"], dependencies=["PlanHdfExists"])
class PrecipHydrographs(RasqcChecker):
    """Checker for precipitation hydrographs.

    Reports the boundary condition precipitation hydrographs applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Precipitation Hydrographs"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Execute precipitation hydrographs check for a RAS plan HDF file.

        Parameters
        ----------
            plan_hdf: The HEC-RAS plan HDF file to check.

            plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        precip_hydrographs_path = BC_PATH + "/Precipitation Hydrographs"
        attrs = ["2D Flow Area"]
        if plan_hdf:
            if precip_hydrographs_path in plan_hdf:
                for p in plan_hdf[precip_hydrographs_path].values():
                    msg = dumps(
                        {k: v for k, v in p.attrs.items() if k in attrs}
                        | {"Depth": round(float(p[:, 1].sum()), 3)},
                        cls=RasqcResultEncoder,
                    )
            else:
                msg = "No precip hydrograph applied."
        else:
            msg = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the precipitation hydrographs for all RAS plan HDF files in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        results = []
        for plan_file in ras_model.plans:
            plan_hdf = plan_file.hdf
            results.append(self._check(plan_hdf, Path(plan_file.hdf_path).name))
        return results


@register_check(["ble"], dependencies=["PlanHdfExists"])
class FlowHydrographs(RasqcChecker):
    """Checker for flow hydrographs.

    Reports the boundary condition flow hydrographs applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Flow Hydrographs"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Execute flow hydrographs check for a RAS plan HDF file.

        Parameters
        ----------
        plan_hdf: The HEC-RAS plan HDF file to check.

        plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        flow_hydrographs_path = BC_PATH + "/Flow Hydrographs"
        attrs = ["2D Flow Area", "BC Line", "EG Slope For Distributing Flow"]
        if plan_hdf:
            if flow_hydrographs_path in plan_hdf:
                for p in plan_hdf[flow_hydrographs_path].values():
                    msg = dumps(
                        {k: v for k, v in p.attrs.items() if k in attrs}
                        | {"Peak Flow": round(float(p[:, 1].max()), 3)},
                        cls=RasqcResultEncoder,
                    )
            else:
                msg = "No flow hydrograph applied."
        else:
            msg = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the flow hydrographs for all RAS plan HDF files in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        results = []
        for plan_file in ras_model.plans:
            plan_hdf = plan_file.hdf
            results.append(self._check(plan_hdf, Path(plan_file.hdf_path).name))
        return results


@register_check(["ble"], dependencies=["PlanHdfExists"])
class StageHydrographs(RasqcChecker):
    """Checker for stage hydrographs.

    Reports the boundary condition stage hydrographs applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Stage Hydrographs"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Execute stage hydrographs check for a RAS plan HDF file.

        Parameters
        ----------
        plan_hdf: The HEC-RAS plan HDF file to check.

        plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        stage_hydrographs_path = BC_PATH + "/Stage Hydrographs"
        attrs = ["2D Flow Area", "BC Line", "Use Initial Stage"]
        if plan_hdf:
            if stage_hydrographs_path in plan_hdf:
                for p in plan_hdf[stage_hydrographs_path].values():
                    msg = dumps(
                        {k: v for k, v in p.attrs.items() if k in attrs}
                        | {"Peak Stage": round(float(p[:, 1].max()), 3)},
                        cls=RasqcResultEncoder,
                    )
            else:
                msg = "No stage hydrograph applied."
        else:
            msg = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the stage hydrographs for all RAS plan HDF files in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        results = []
        for plan_file in ras_model.plans:
            plan_hdf = plan_file.hdf
            results.append(self._check(plan_hdf, Path(plan_file.hdf_path).name))
        return results


@register_check(["ble"], dependencies=["PlanHdfExists"])
class NormalDepths(RasqcChecker):
    """Checker for normal depths.

    Reports the boundary condition normal depths applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Normal Depths"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Execute normal depths check for a RAS plan HDF file.

        Parameters
        ----------
        plan_hdf: The HEC-RAS plan HDF file to check.

        plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        normal_depths_path = BC_PATH + "/Normal Depths"
        attrs = ["2D Flow Area", "BC Line", "BC Line WS"]
        if plan_hdf:
            if normal_depths_path in plan_hdf:
                for p in plan_hdf[normal_depths_path].values():
                    msg = dumps(
                        {k: v for k, v in p.attrs.items() if k in attrs}
                        | {"Normal Depth Slope": float(p[0])},
                        cls=RasqcResultEncoder,
                    )
            else:
                msg = "No normal depth applied."
        else:
            msg = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the normal depths for all RAS plan HDF files in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        results = []
        for plan_file in ras_model.plans:
            plan_hdf = plan_file.hdf
            results.append(self._check(plan_hdf, Path(plan_file.hdf_path).name))
        return results


@register_check(["ble"], dependencies=["PlanHdfExists"])
class RatingCurves(RasqcChecker):
    """Checker for rating curves.

    Reports the boundary condition rating curves applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Rating Curves"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Execute rating curves check for a RAS plan HDF file.

        Parameters
        ----------
        plan_hdf: The HEC-RAS plan HDF file to check.

        plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        rating_curves_path = BC_PATH + "/Rating Curves"
        attrs = ["2D Flow Area", "BC Line"]
        if plan_hdf:
            if rating_curves_path in plan_hdf:
                for p in plan_hdf[rating_curves_path].values():
                    msg = dumps(
                        {k: v for k, v in p.attrs.items() if k in attrs},
                        cls=RasqcResultEncoder,
                    )
            else:
                msg = "No rating curve applied."
        else:
            msg = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the rating curves for all RAS plan HDF files in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        results = []
        for plan_file in ras_model.plans:
            plan_hdf = plan_file.hdf
            results.append(self._check(plan_hdf, Path(plan_file.hdf_path).name))
        return results


@register_check(["ble"], dependencies=["PlanHdfExists"])
class InitialConditions(RasqcChecker):
    """Checker for initial conditions.

    Reports the initial conditions applied to the HEC-RAS model. Result status is 'note'.
    """

    name = "Initial Conditions"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Execute initial conditions check for a RAS plan HDF file.

        Parameters
        ----------
        plan_hdf: The HEC-RAS plan HDF file to check.

        plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        ic_name_path = IC_PATH + "/IC Point Names"
        ic_elev_path = IC_PATH + "/IC Point Elevations"
        if plan_hdf:
            if ic_name_path in plan_hdf:
                msg = dumps(
                    {
                        k.decode(): round(v, 3)
                        for k, v in zip(plan_hdf[ic_name_path], plan_hdf[ic_elev_path])
                    },
                    cls=RasqcResultEncoder,
                )
            else:
                msg = "No initial conditions applied."
        else:
            msg = "No HDF file located."
        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.NOTE,
            message=msg,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the initial conditions for all RAS plan HDF files in a model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: A list of the results of the checks.
        """
        results = []
        for plan_file in ras_model.plans:
            plan_hdf = plan_file.hdf
            results.append(self._check(plan_hdf, Path(plan_file.hdf_path).name))
        return results
