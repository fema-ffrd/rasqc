"""Naming convention checkers for FFRD HEC-RAS models."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel, RasModelFile
from ..result import RasqcResult, ResultStatus

from jsonschema import validate, ValidationError
from rashdf import RasGeomHdf

from datetime import date
import importlib.resources
import json
from typing import Any, List


def _load_schema() -> dict:
    """Load the JSON schema for naming conventions."""
    with importlib.resources.path("rasqc.data", "naming-schema.json") as path:
        with open(path) as f:
            return json.load(f)


NAMING_SCHEMA = _load_schema()


def _get_schema(property_name: str) -> dict:
    """Get a property from the naming schema."""
    return NAMING_SCHEMA["properties"][property_name]


class JsonSchemaChecker(RasqcChecker):
    """Base class for JSON schema checks."""

    schema_property: str

    def _check(self, s: str, filename: str) -> RasqcResult:
        """Run the check."""
        schema = _get_schema(self.schema_property)
        try:
            validate(s, schema)
            return RasqcResult(
                name=self.name, filename=filename, result=ResultStatus.OK
            )
        except ValidationError:
            if "description" in schema:
                err_msg = f"'{s}': {schema['description']}"
            else:
                err_msg = f"'{s}': {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.ERROR,
                message=err_msg,
                pattern=schema.get("pattern"),
            )


@register_check(["ffrd"])
class PrjFilenamePattern(JsonSchemaChecker):
    """Checker for project filename pattern."""

    name = "Project filename pattern"
    criteria = (
        "Project filename should follow the pattern 'subbasin-name.prj',"
        " where the subbasin name is all lowercase letters and hyphens."
    )
    schema_property = "project_file_name"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Check if the project filename follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        filename = ras_model.prj_file.path.name
        return self._check(filename, filename)


@register_check(["ffrd"])
class GeometryTitlePattern(JsonSchemaChecker):
    """Checker for geometry file title naming conventions."""

    name = "Geometry title pattern"
    criteria = (
        "Geometry file title should follow the pattern 'subbasin-name',"
        " where the subbasin name is all lowercase letters and hyphens."
    )
    schema_property = "geometry_name"

    def run(self, ras_model: RasModel) -> RasqcResult:
        """Check if the geometry file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(g.title, g.path.name) for g in ras_model.geometries]


@register_check(["ffrd"])
class UnsteadyFlowTitlePattern(JsonSchemaChecker):
    """Checker for unsteady flow file title naming conventions."""

    name = "Unsteady Flow title pattern"
    criteria = "Unsteady Flow file title should follow the pattern 'YYYY-MM-DD'."
    schema_property = "unsteady_flow_name"

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the unsteady flow file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(u.title, u.path.name) for u in ras_model.unsteadies]


@register_check(["ffrd"])
class PlanTitlePattern(JsonSchemaChecker):
    """Checker for plan file title naming conventions."""

    name = "Plan title pattern"
    criteria = (
        "Plan file title should follow the naming convention "
        "'hydra-event-type:YYYY-MM-DD', where 'hydra-event-type'"
        " is a lowercase description "
    )
    schema_property = "plan_name"

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the plan file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(p.title, p.path.name) for p in ras_model.plans]


@register_check(["ffrd"])
class PlanShortIdPattern(JsonSchemaChecker):
    """Checker for plan file short ID naming conventions."""

    name = "Plan short ID pattern"
    criteria = (
        "Plan file short ID should follow the naming convention "
        "'hydra-event-type:YYYY-MM-DD', where 'hydra-event-type'"
        " is a lowercase description "
    )
    schema_property = "plan_short_id"

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the plan file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        return [self._check(p.short_id, p.path.name) for p in ras_model.plans]


@register_check(["ffrd"])
class D2FlowArea(JsonSchemaChecker):
    """Checker for 2D Flow Area naming conventions."""

    name = "2D Flow Area pattern"
    criteria = (
        "2D Flow Area names should follow the naming convention "
        "'subbasin-name[_1]', where '[_1]' is an optional suffix "
        " for multiple 2D Flow Areas in the same geometry."
    )
    schema_property = "2d_flow_element"

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the plan file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        results = []
        for geom in ras_model.geometries:
            if geom.hdf:
                results.extend(
                    [
                        self._check(m, geom.hdf_path.name)
                        for m in geom.hdf.mesh_area_names()
                    ]
                )
        return results


@register_check(["ffrd"])
class TerrainNamePattern(JsonSchemaChecker):
    """Checker for terrain file naming conventions."""

    name = "Terrain name pattern"
    criteria = (
        "Terrain file name should follow the naming convention "
        "'subbasin-name[_1]', where '[_1]' is an optional suffix "
        " for multiple terrain files in the same geometry."
    )
    schema_property = "terrain_name"

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the terrain file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        results = []
        for geom in ras_model.geometries:
            if geom.hdf:
                geom_attrs = geom.hdf.get_geom_attrs()
                terrain_name = geom_attrs.get("Terrain Layername")
                if terrain_name:
                    results.append(self._check(terrain_name, geom.hdf_path.name))
                else:
                    results.append(
                        RasqcResult(
                            name=self.name,
                            filename=geom.hdf_path.name,
                            result=ResultStatus.ERROR,
                            message="Terrain Layerame not found in geometry HDF file.",
                        )
                    )
        return results


@register_check(["ffrd"])
class ReferenceLinePattern(JsonSchemaChecker):
    """Checker for reference line naming conventions."""

    name = "Reference Line pattern"
    criteria = (
        "Reference Line names should follow the naming convention "
        "'subbasin-name[_1]', where '[_1]' is an optional suffix "
        " for multiple reference lines in the same geometry."
    )
    schema_property = "ref_line_gage"

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the reference line title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        results = []
        for geom in ras_model.geometries:
            if geom.hdf:
                for mesh in geom.hdf.mesh_area_names():
                    reflines = geom.hdf.reference_lines_names(mesh)
                    for ref_line in reflines:
                        results.append(self._check(ref_line, geom.hdf_path.name))
        return results


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
            err_msg = f"{[g.path.suffix for g in geom_files]}: {self.criteria}"
            return RasqcResult(
                name=self.name,
                filename=ras_model.prj_file.path.name,
                result=ResultStatus.ERROR,
                message=err_msg,
            )
        return RasqcResult(
            name=self.name,
            filename=ras_model.prj_file.path.name,
            result=ResultStatus.OK,
        )


@register_check(["ffrd"])
class GeometryTitleMatchesProject(RasqcChecker):
    """Checker for geometry file title naming conventions."""

    name = "Geometry title matches project"
    criteria = "Geometry file title should match the project filename."

    def _check(self, prj_filename: str, geom_file: RasModelFile) -> RasqcResult:
        """Check if the geometry file title matches the project filename.

        Parameters
        ----------
            geom_file: The geometry file to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
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

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the geometry file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        results = [
            self._check(ras_model.prj_file.path.name, g) for g in ras_model.geometries
        ]
        return results


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
