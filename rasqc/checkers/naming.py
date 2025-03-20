"""Naming convention checkers for FFRD HEC-RAS models."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel, RasModelFile
from ..result import RasqcResult, ResultStatus

from datetime import date
import re
from typing import List


@register_check(["ffrd"])
class PrjFilenamePattern(RasqcChecker):
    """Checker for project filename pattern."""

    name = "Project filename pattern"
    criteria = ("Project filename should follow the pattern 'subbasin-name.prj',"
                " where the subbasin name is all lowercase letters and hyphens.")

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Check if the project file follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        filename = ras_model.prj_file.path.name
        if not re.match(r"[a-z0-9-].prj", filename):
            err_msg = f"'{filename}': {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.ERROR,
                message=err_msg
            )
        return RasqcResult(name=self.name, filename=filename, result=ResultStatus.OK)


@register_check(["ffrd"])
class SingleGeometryFile(RasqcChecker):
    """Checker for single geometry file in the project."""

    name = "Single Geometry file"
    criteria = "There should be only one geometry file in the project."

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Check if there is only one geometry file in the project.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        geom_files = ras_model.geometries
        if len(geom_files) != 1:
            err_msg = f"'{len(geom_files)}': {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=ras_model.prj_file.path.name,
                result=ResultStatus.ERROR,
                message=err_msg,
            )
        return RasqcResult(
            name=self.name, filename=geom_files[0].path.name, result=ResultStatus.OK
        )


@register_check(["ffrd"])
class GeometryTitleMatchesProject(RasqcChecker):
    """Checker for geometry file title naming conventions."""

    name = "Geometry title matches project"
    criteria = "Geometry file title should match the project filename."

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Check if the geometry file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        prj_filename = ras_model.prj_file.path.name
        geom_file = ras_model.current_geometry
        geom_title = geom_file.title
        if not geom_title == prj_filename[:-4]:
            err_msg = f"'{geom_title}': {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=geom_file.path.name,
                result=ResultStatus.ERROR,
                message=err_msg,
            )
        return RasqcResult(
            name=self.name, filename=geom_file.path.name, result=ResultStatus.OK
        )


@register_check(["ffrd"])
class UnsteadyFlowNamePattern(RasqcChecker):
    """Checker for unsteady flow file title naming conventions."""

    name = "Unsteady Flow title name pattern"
    criteria = "Unsteady Flow file title should follow the pattern 'YYYY-MM-DD'."

    def _check(self, unsteady_flow_file: RasModelFile) -> RasqcResult:
        """Check if the unsteady flow file title follows the naming convention.

        Parameters
        ----------
            unsteady_flow_file: The unsteady flow file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        flow_title = unsteady_flow_file.title
        if not re.match(r"\d{4}-\d{2}-\d{2}", flow_title):
            err_msg = f"'{flow_title}': {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=unsteady_flow_file.path.name,
                result=ResultStatus.ERROR,
                message=err_msg,
            )
        return RasqcResult(
            name=self.name,
            filename=unsteady_flow_file.path.name,
            result=ResultStatus.OK,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the unsteady flow file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(u) for u in ras_model.unsteadies]


@register_check(["ffrd"])
class UnsteadyFlowTitleValidDate(RasqcChecker):
    """Check if unsteady flow files have titles with valid dates."""

    name = "Unsteady Flow title valid date"
    criteria = "Unsteady Flow file title should be a valid date in ISO 8601 format."

    def _check(self, unsteady_flow_file: RasModelFile) -> RasqcResult:
        """Check if the unsteady flow file title is a valid date.

        Parameters
        ----------
            unsteady_flow_file: The unsteady flow file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        flow_title = unsteady_flow_file.title
        try:
            date.fromisoformat(flow_title)
        except ValueError:
            err_msg = f"'{flow_title}': {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=unsteady_flow_file.path.name,
                result=ResultStatus.ERROR,
                message=err_msg,
            )
        return RasqcResult(
            name=self.name,
            filename=unsteady_flow_file.path.name,
            result=ResultStatus.OK,
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the unsteady flow file title is a valid date.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(u) for u in ras_model.unsteadies]


@register_check(["ffrd"])
class PlanTitleNamePattern(RasqcChecker):
    """Checker for plan file title naming conventions."""

    name = "Plan title naming"
    criteria = ("Plan file title should follow the naming convention "
                "'hydra-event-type:YYYY-MM-DD', where 'hydra-event-type'"
                " is a lowercase description ")

    def _check(self, plan_file: RasModelFile) -> RasqcResult:
        plan_title = plan_file.title
        match = re.match(r"[a-z0-9-]*:\d{4}-\d{2}-\d{2}", plan_title)
        if not match:
            err_msg = f"'{plan_title}': {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=plan_file.path.name,
                result=ResultStatus.ERROR,
                message=err_msg,
            )
        return RasqcResult(
            name=self.name, filename=plan_file.path.name, result=ResultStatus.OK
        )

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the plan file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(p) for p in ras_model.plans]