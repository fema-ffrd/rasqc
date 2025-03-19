"""Naming convention checkers for FFRD HEC-RAS models."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel
from ..result import RasqcResult, ResultStatus

import re


@register_check(["ffrd"])
class PrjFileNaming(RasqcChecker):
    """Checker for project file naming conventions.

    Checks if the project file follows the naming convention:
    'Basin_Name_<HUC4-ID>_Subbasin_name.prj'
    """

    name = "Project file naming"

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
        if not re.match(r"\w*_\d{4}_\w*\.prj", filename):
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS project file '{filename}' does not follow the"
                    " naming convention 'Basin_Name_<HUC4-ID>_Subbasin_name.prj',"
                    " where <HUC4-ID> is a 4-digit HUC number."
                ),
            )
        return RasqcResult(name=self.name, filename=filename, result=ResultStatus.OK)


@register_check(["ffrd"])
class GeometryTitleNaming(RasqcChecker):
    """Checker for geometry file title naming conventions.

    Checks if the geometry file title follows the naming convention:
    'Watershed Name FFRD'
    """

    name = "Geometry title naming"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Check if the geometry file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        geom_file = ras_model.current_geometry
        geom_title = geom_file.title
        if not re.match(r"\w* FFRD$", geom_title):
            return RasqcResult(
                name=self.name,
                filename=geom_file.path.name,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS geometry file title '{geom_title}' does not follow the"
                    f" naming convention 'Watershed Name FFRD' ({geom_file.path.name})"
                ),
            )
        return RasqcResult(
            name=self.name, filename=geom_file.path.name, result=ResultStatus.OK
        )


@register_check(["ffrd"])
class PlanTitleNaming(RasqcChecker):
    """Checker for plan file title naming conventions.

    Checks if the plan file title follows the naming convention:
    'MonYEAR Event' (e.g., 'Jan2023 100yr')
    """

    name = "Plan title naming"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Check if the plan file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        plan_file = ras_model.current_plan
        plan_title = plan_file.title
        match = re.match(r"(\w{3})(\d{4}) .*$", plan_title)
        if not match:
            return RasqcResult(
                name=self.name,
                filename=plan_file.path.name,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS plan file title '{plan_title}' does not follow the"
                    f" naming convention 'MonYEAR Event' ({plan_file.path.name})"
                ),
            )
        return RasqcResult(
            name=self.name, filename=plan_file.path.name, result=ResultStatus.OK
        )


@register_check(["ffrd"])
class UnsteadyFlowTitleNaming(RasqcChecker):
    """Checker for unsteady flow file title naming conventions.

    Checks if the unsteady flow file title follows the naming convention:
    'MonYEAR' (e.g., 'Jan2023')
    """

    name = "Unsteady flow title naming"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Check if the unsteady flow file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        flow_file = ras_model.current_unsteady
        flow_title = flow_file.title
        match = re.match(r"(\w{3})(\d{4})", flow_title)
        if not match:
            return RasqcResult(
                name=self.name,
                filename=flow_file.path.name,
                result=ResultStatus.ERROR,
                message=(
                    f"HEC-RAS unsteady flow file title '{flow_title}' does not follow the"
                    f" naming convention 'MonYEAR' ({flow_file.path.name})"
                ),
            )
        return RasqcResult(
            name=self.name, filename=flow_file.path.name, result=ResultStatus.OK
        )
