"""Module for checking that the runtime is long enough to route the peak at the outflow boundary."""

from rasqc.base_checker import RasqcChecker
from rasqc.registry import register_check
from rasqc.result import RasqcResult, ResultStatus, RasqcResultEncoder
from rasqc.rasmodel import RasModel

from rashdf import RasPlanHdf

from json import dumps
from typing import List
from pathlib import Path


@register_check(["ble"], dependencies=["PlanHdfExists"])
class PeakRouted(RasqcChecker):
    """Checker for ensuring the runtime is long enough to route the peak at the outflow boundary."""

    name = "Peak Routed"

    def _check(self, plan_hdf: RasPlanHdf, plan_hdf_filename: str) -> RasqcResult:
        """Check if the runtime is long enough to route the peak at the outflow boundary for a RAS plan HDF file.

        Parameters
        ----------
            plan_hdf: The HEC-RAS plan HDF file to check.

            plan_hdf_filename: The file name of the HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        if not plan_hdf:
            return RasqcResult(
                name=self.name,
                filename=plan_hdf_filename,
                result=ResultStatus.WARNING,
                message="Plan HDF file not found.",
            )

        bc_lines = plan_hdf.bc_lines_timeseries_output()
        if not bc_lines:
            return RasqcResult(
                name=self.name,
                filename=plan_hdf_filename,
                result=ResultStatus.WARNING,
                message="No boundary condition lines found.",
            )

        msg_dict = {}
        for bc_line_id in bc_lines.bc_line_id.values:
            # Get the flow time series for this bc_line_id
            bc_line_name = str(bc_lines.bc_line_name.sel(bc_line_id=bc_line_id).values)
            flow_timeseries = bc_lines.Flow.sel(bc_line_id=bc_line_id)

            # Find the peak flow value and time
            peak_flow = int(flow_timeseries.max().values)
            peak_index = int(flow_timeseries.argmax(dim="time").values)
            peak_time = str(flow_timeseries.time.values[peak_index])
            total_timesteps = len(flow_timeseries.time)

            if peak_index >= total_timesteps - 4:
                msg_dict[bc_line_name] = (
                    f"WARNING: Peak flow may not be routed before the end of the simulation."
                )
            else:
                msg_dict[bc_line_name] = (
                    f"OK: Peak flow {peak_flow} occurs at {peak_time} (time index {peak_index} of {total_timesteps})."
                )

        return RasqcResult(
            name=self.name,
            filename=plan_hdf_filename,
            result=ResultStatus.OK,
            message=dumps(msg_dict, cls=RasqcResultEncoder),
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the routed peaks for all plans in a model.

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
