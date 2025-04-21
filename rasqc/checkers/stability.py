"""Classes for checking stability of model runs."""

import hydrostab.ras
from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

from rashdf import RasPlanHdf

import os
import itertools
from typing import Dict, List

STABILITY_VARS = [
    "Water Surface",
    "Flow",
]
UNSTABLE_THRESHOLD = 0.002  # 0.002 is the default for hydrostab


@register_check(["ffrd"])
class ReflineStability(RasqcChecker):
    """Reference lines stability checker.

    Checks if the reference line is stable based on the stability analysis results.
    """

    name = "Reference Line Stability Analysis"

    def _check(self, phdf: RasPlanHdf) -> List[RasqcResult]:
        """Check the stability of reference line hydrographs.

        Parameters
        ----------
            phdf: The HEC-RAS Plan HDF file to check.

        Returns
        -------
            List[RasqcResult]: Results of the stability check.
        """
        ds_refline_stability = hydrostab.ras.reflines_stability(
            phdf, unstable_threshold=UNSTABLE_THRESHOLD
        )
        refline_names = ds_refline_stability.coords["refln_name"].values
        refline_ids = ds_refline_stability.coords["refln_id"].values
        filename = os.path.basename(phdf._loc)
        results = []
        for id, name in zip(refline_ids, refline_names):
            for var in STABILITY_VARS:
                da_is_stable = ds_refline_stability[f"{var} is Stable"]
                da_score = ds_refline_stability[f"{var} Stability Score"]
                is_stable = da_is_stable.sel(refln_id=id).all()
                stability_score = da_score.sel(refln_id=id).values
                if is_stable:
                    results.append(
                        RasqcResult(
                            name=self.name + f" - {var}",
                            element=name,
                            result=ResultStatus.OK,
                            filename=filename,
                        )
                    )
                else:
                    results.append(
                        RasqcResult(
                            name=self.name + f" - {var}",
                            element=name,
                            result=ResultStatus.WARNING,
                            filename=filename,
                            message=(
                                f"Reference line '{name}': potential {var} hydrograph instability detected."
                                f" (score: {stability_score} >= {UNSTABLE_THRESHOLD})"
                            ),
                        )
                    )
        return results

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the stability of reference line hydrographs.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResults]: Results of the stability check.
        """
        results = []
        for plan in ras_model.plans:
            phdf = plan.hdf
            if not phdf:
                continue
            # If there are no reference lines, skip the check
            reflines_names: Dict[str, List[str]] = phdf.reference_lines_names()
            names = list(itertools.chain(*reflines_names.values()))
            if len(names) == 0:
                continue
            result = self._check(phdf)
            results.extend(result)
        return results


@register_check(["ffrd"])
class RefpointStability(RasqcChecker):
    """Reference points stability checker.

    Checks if the reference point is stable based on the stability analysis results.
    """

    def _check(self, phdf: RasPlanHdf) -> List[RasqcResult]:
        """Check the stability of reference point hydrographs.

        Parameters
        ----------
            phdf: The HEC-RAS Plan HDF file to check.

        Returns
        -------
            List[RasqcResult]: Results of the stability check.
        """
        ds_refpoint_stability = hydrostab.ras.refpoints_stability(
            phdf, unstable_threshold=UNSTABLE_THRESHOLD
        )
        refpoint_names = ds_refpoint_stability.coords["refpt_name"].values
        refpoint_ids = ds_refpoint_stability.coords["refpt_id"].values
        filename = os.path.basename(phdf._loc)
        results = []
        for id, name in zip(refpoint_ids, refpoint_names):
            for var in STABILITY_VARS:
                da_is_stable = ds_refpoint_stability[f"{var} is Stable"]
                da_score = ds_refpoint_stability[f"{var} Stability Score"]
                is_stable = da_is_stable.sel(refpt_id=id).all()
                stability_score = da_score.sel(refpt_id=id).values
                if is_stable:
                    results.append(
                        RasqcResult(
                            name="Reference Point Stability Analysis - " + var,
                            element=name,
                            result=ResultStatus.OK,
                            filename=filename,
                        )
                    )
                else:
                    results.append(
                        RasqcResult(
                            name="Reference Point Stability Analysis - " + var,
                            element=name,
                            result=ResultStatus.WARNING,
                            filename=filename,
                            message=(
                                f"Reference point '{name}': potential {var} hydrograph instability detected."
                                f" (score: {stability_score} >= {UNSTABLE_THRESHOLD})"
                            ),
                        )
                    )
        return results

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the stability of reference point hydrographs.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: Results of the stability check.
        """
        results = []
        for plan in ras_model.plans:
            phdf = plan.hdf
            if not phdf:
                continue
            # If there are no reference lines, skip the check
            refpoints_names: Dict[str, List[str]] = phdf.reference_points_names()
            names = list(itertools.chain(*refpoints_names.values()))
            if len(names) == 0:
                continue
            result = self._check(phdf)
            results.extend(result)
        return results


# TODO: See what we can do to either significantly improve the runtime of this or make it optional.
# Currently, this check takes a long time to run on large models.
# For now, ommitting this from the default FFRD checks.
# @register_check(["ffrd"])
class MeshCellsStability(RasqcChecker):
    """Mesh Cells Stability checker.

    Checks stability of a model's mesh cell hydrographs.
    """

    name = "Mesh Cells Stability Analysis"

    def _check_mesh_area(self, phdf: RasPlanHdf, mesh_name: str) -> List[RasqcResult]:
        results = []
        ds = hydrostab.ras.mesh_cells_stability(
            phdf, mesh_name=mesh_name, unstable_threshold=UNSTABLE_THRESHOLD
        )
        for var in STABILITY_VARS:
            da = ds[var]
            da_is_stable = da[f"{var} is Stable"]
            unstable_count = da_is_stable[da_is_stable == False].size
            unstable_pct = unstable_count / da.size * 100
            if unstable_count > 0:
                results.append(
                    RasqcResult(
                        name=self.name,
                        result=ResultStatus.ERROR,
                        filename=phdf.filename,
                        message=f"Mesh '{mesh_name}': {unstable_count} unstable cells ({unstable_pct}%).",
                    )
                )
            results.append(
                RasqcResult(
                    name=self.name,
                    result=ResultStatus.OK,
                    filename=phdf.filename,
                )
            )
        return results

    def _check(self, phdf: RasPlanHdf) -> List[RasqcResult]:
        """Check the stability of the model runs.

        Parameters
        ----------
            phdf: The HEC-RAS plan HDF file to check.

        Returns
        -------
            RasqcResult: The result of the stability check.
        """
        mesh_area_names = phdf.mesh_area_names()
        stability = []
        for mesh_name in mesh_area_names:
            stability.extend(self._check_mesh_area(phdf, mesh_name))
        return stability

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check the stability of the model mesh cell hydrographs.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            List[RasqcResult]: The results of the stability check.
        """
        results = []
        for plan in ras_model.plans:
            phdf = plan.hdf
            if not phdf:
                continue
            result = self._check(phdf)
            results.extend(result)
        return results
