"""Checks to confirm if HDF5 output files are in sync with HEC-RAS model."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel, RasModelFile, GeomFile, PlanFile
from ..result import RasqcResult, ResultStatus

from rashdf import RasGeomHdf, RasPlanHdf

from pathlib import Path
from typing import List


@register_check(["ffrd"])
class GeomHdfExists(RasqcChecker):
    """Check if each Geometry file has a corresponding HDF file."""

    name = "Geometry HDF file exists"
    criteria = "Each Geometry file should have a corresponding HDF file."

    def _check(self, geom_file: GeomFile) -> RasqcResult:
        """Check if the Geometry file has a corresponding HDF file."""
        hdf_path = Path(f"{geom_file.path}.hdf")
        if not hdf_path.exists():
            err_msg = f"{geom_file.path.name}: {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=hdf_path.name,
                result=ResultStatus.ERROR,
                message=err_msg,
            )
        return RasqcResult(
            name=self.name,
            filename=hdf_path.name,
            result=ResultStatus.OK,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the Geometry HDF file is in sync with the HEC-RAS model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(geom_file) for geom_file in ras_model.geometries]


@register_check(["ffrd"])
class GeomHdfDatetime(RasqcChecker):
    """Check if the HDF file datetime aligns with Geometry file datetime."""

    name = "Geometry HDF file datetime"
    criteria = (
        "Geometry HDF file datetime should be newer than the last Geometry file update."
    )

    def _check(self, geom_file: GeomFile) -> RasqcResult:
        """Check if the HDF file datetime aligns with the Geometry file datetime."""
        geom_file_last_updated = geom_file.last_updated()
        hdf_path = Path(f"{geom_file.path}.hdf")
        ghdf = RasGeomHdf(hdf_path)
        ghdf_attrs = ghdf.get_geom_attrs()
        ghdf_datetime = ghdf_attrs.get("Geometry Time")
        if geom_file_last_updated > ghdf_datetime:
            err_msg = f"'{geom_file.path.name}': {self.criteria} ({geom_file_last_updated} > {ghdf_datetime})"
            return RasqcResult(
                name=self.name,
                filename=hdf_path.name,
                result=ResultStatus.ERROR,
                message=err_msg,
            )
        return RasqcResult(
            name=self.name,
            filename=hdf_path.name,
            result=ResultStatus.OK,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the HDF file datetime aligns with the Geometry file datetime.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(geom_file) for geom_file in ras_model.geometries]


@register_check(["ffrd"])
class PlanHdfExists(RasqcChecker):
    """Check if each Plan file has a corresponding HDF file."""

    name = "Plan HDF file exists"
    criteria = "Each Plan file should have a corresponding HDF file."

    def _check(self, plan_file: RasModelFile) -> RasqcResult:
        """Check if the Plan file has a corresponding HDF file."""
        hdf_path = Path(f"{plan_file.path}.hdf")
        if not hdf_path.exists():
            err_msg = f"{plan_file.path.name}: {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=hdf_path.name,
                result=ResultStatus.ERROR,
                message=err_msg,
            )
        return RasqcResult(
            name=self.name,
            filename=hdf_path.name,
            result=ResultStatus.OK,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the Plan HDF file is in sync with the HEC-RAS model.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(plan_file) for plan_file in ras_model.plans]


@register_check(["ffrd"], dependencies=['PlanHdfExists'])
class PlanHdfDatetime(RasqcChecker):
    """Check if the Plan HDF datetime aligns with the associated Geometry file datetime."""

    name = "Plan HDF file datetime"
    criteria = (
        "Plan HDF file datetime should be newer than the Geometry HDF file datetime."
    )

    def _check(self, plan_file: PlanFile) -> RasqcResult:
        """Check if the Plan HDF datetime aligns with the Geometry file datetime."""
        geom_file = plan_file.geom_file
        ghdf_path = Path(f"{geom_file.path}.hdf")
        ghdf = RasPlanHdf(ghdf_path)
        ghdf_attrs = ghdf.get_geom_attrs()
        ghdf_datetime = ghdf_attrs.get("Geometry Time")

        phdf_path = Path(f"{plan_file.path}.hdf")
        if phdf_path.exists():
            phdf = RasPlanHdf(phdf_path)
            phdf_attrs = phdf.get_results_unsteady_summary_attrs()
            run_time_window = phdf_attrs.get("Run Time Window")
            if run_time_window:
                run_time_start = run_time_window[0]
                if run_time_start > ghdf_datetime:
                    err_msg = f"'{plan_file.path.name}': {self.criteria} ({run_time_start} > {ghdf_datetime})"
                    return RasqcResult(
                        name=self.name,
                        filename=phdf_path.name,
                        result=ResultStatus.ERROR,
                        message=err_msg,
                    )
                return RasqcResult(
                    name=self.name,
                    filename=phdf_path.name,
                    result=ResultStatus.OK,
                )
            return RasqcResult(
                name=self.name,
                filename=phdf_path.name,
                result=ResultStatus.ERROR,
                message="Run Time Window not found in HDF file.",
            )
        return RasqcResult(
            name=self.name,
            filename=phdf_path.name,
            result=ResultStatus.ERROR,
            message="HDF file does not exist.",
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the Plan HDF file datetime aligns with the Geometry file datetime.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(plan_file) for plan_file in ras_model.plans]
