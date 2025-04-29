"""Naming convention checkers for FFRD HEC-RAS models."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel, RasModelFile
from ..result import RasqcResult, ResultStatus
from ..constants import RAS_SCHEMA_URL

from jsonschema import validate, ValidationError
from geopandas import GeoDataFrame
from rashdf.utils import convert_ras_hdf_string

from datetime import date
import importlib.resources
import urllib
import json
from typing import List


def load_schema(schema_url: str) -> dict:
    """Load external schema from given url."""
    with urllib.request.urlopen(schema_url) as response:
        return json.load(response)


NAMING_SCHEMA = load_schema(RAS_SCHEMA_URL)


def _get_schema(property_name: str) -> dict:
    """Get a property from the naming schema."""
    return NAMING_SCHEMA["properties"][property_name]


class JsonSchemaChecker(RasqcChecker):
    """Base class for JSON schema checks."""

    schema_property: str
    criteria: str

    def _check(self, s: str, filename: str) -> RasqcResult:
        """Run the check."""
        schema = _get_schema(self.schema_property)
        try:
            validate(s, schema)
            return RasqcResult(name=self.name, filename=filename, result=ResultStatus.OK)
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
                examples=schema.get("examples"),
            )


class MultiJsonSchemaChecker(JsonSchemaChecker):
    """Base class for multiple JSON schema checks."""

    schema_properties: List[str]
    criteria: str

    def _check(self, s: str, filename: str) -> RasqcResult:
        """Run the check."""
        patterns = []
        examples = []
        for prop in self.schema_properties:
            schema = _get_schema(prop)
            pattern = schema.get("pattern")
            patterns.append(pattern)
            examples.extend(schema.get("examples", []))
            try:
                validate(s, schema)
                return RasqcResult(
                    name=self.name,
                    filename=filename,
                    result=ResultStatus.OK,
                    pattern=pattern,
                )
            except ValidationError:
                pass
        return RasqcResult(
            name=self.name,
            filename=filename,
            result=ResultStatus.ERROR,
            message=f"'{s}': {self.criteria}",
            pattern=patterns,
            examples=examples,
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
    schema_property = "geometry_title"

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
    schema_property = "unsteady_flow_title"

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
    schema_property = "plan_title"

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


@register_check(["ffrd"], dependencies=["GeomHdfExists"])
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


@register_check(["ffrd"], dependencies=["GeomHdfExists"])
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
                results.extend([self._check(m, geom.hdf_path.name) for m in geom.hdf.mesh_area_names()])
        return results


@register_check(["ffrd"], dependencies=["GeomHdfExists"])
class ExternalBoundaryConditionLinePattern(MultiJsonSchemaChecker):
    """Checker for boundary condition line naming conventions."""

    name = "External Boundary Condition line name pattern"
    criteria = (
        "Boundary Condition line names should follow naming conventions"
        " for inflow from RAS, outflow to RAS, inflow from HMS, and outflow to HMS."
    )
    schema_properties = [
        "inflow_bc_from_ras",
        "outflow_bc_to_ras",
        "outflow_bc",
    ]

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the boundary condition line title follows the naming convention.

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
                bc_lines: GeoDataFrame = geom.hdf.bc_lines()
                if not bc_lines.empty:
                    bc_lines_names = bc_lines[bc_lines["type"] == "External"]["name"]
                    for bc_line_name in bc_lines_names:
                        results.append(self._check(bc_line_name, geom.hdf_path.name))
        return results


@register_check(["ffrd"], dependencies=["GeomHdfExists"])
class InternalBoundaryConditionLinePattern(JsonSchemaChecker):
    """Checker for internal boundary condition line naming conventions."""

    name = "Internal Boundary Condition line name pattern"
    criteria = (
        "Internal Boundary Condition Lines should follow naming conventions"
        " for an internal boundary condition from HMS."
    )
    schema_property = "internal_bc_from_hms"

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the internal boundary condition line title follows the naming convention.

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
                bc_lines: GeoDataFrame = geom.hdf.bc_lines()
                if not bc_lines.empty:
                    bc_lines_names = bc_lines[bc_lines["type"] == "Internal"]["name"]
                    for bc_line_name in bc_lines_names:
                        results.append(self._check(bc_line_name, geom.hdf_path.name))
        return results


@register_check(["ffrd"], dependencies=["PlanHdfExists"])
class PrecipBoundaryConditionPattern(JsonSchemaChecker):
    """Checker for precipitation boundary condition DSS path conventions."""

    name = "Precip Boundary Condition name pattern"
    criteria = (
        "Precip Boundary Condition names should follow naming conventions" " for precipitation boundary conditions."
    )
    schema_property = "precip_bc"

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the precipitation boundary condition title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        results = []
        for plan in ras_model.plans:
            if plan.hdf:
                met_attrs = plan.hdf.get_meteorology_precip_attrs()
                dss_path = met_attrs.get("DSS Pathname")
                if dss_path:
                    results.append(self._check(dss_path, plan.hdf_path.name))
                else:
                    results.append(
                        RasqcResult(
                            name=self.name,
                            filename=plan.hdf_path.name,
                            result=ResultStatus.ERROR,
                            message="Precipitation DSS Path not found in Plan HDF file.",
                        )
                    )
        return results


@register_check(["ffrd"], dependencies=["GeomHdfExists"])
class InitialConditionPointPattern(JsonSchemaChecker):
    """Checker for initial condition point naming conventions."""

    name = "Initial Condition Point name pattern"
    criteria = "Initial Condition Point names should follow naming conventions" " for initial condition points."
    schema_property = "initial_condition_point_name"

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the initial condition point title follows the naming convention.

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
                ic_points = geom.hdf.get("Geometry/IC Points/Attributes")
                if ic_points:
                    ic_points_names = ic_points[()]["Name"]
                    for ic_point_name in ic_points_names:
                        results.append(
                            self._check(
                                convert_ras_hdf_string(ic_point_name),
                                geom.hdf_path.name,
                            )
                        )
        return results


@register_check(["ffrd"], dependencies=["GeomHdfExists"])
class SA2DConnectionPattern(MultiJsonSchemaChecker):
    """Checker for SA/2D Connection naming conventions."""

    name = "SA/2D Connection name pattern"
    criteria = "SA/2D Connection names should follow naming conventions for SA/2D Connections."
    schema_properties = [
        "dam_connection",
        "levee_connection",
        "other_connection",
    ]

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the 2D connection title follows the naming convention.

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
                structures = geom.hdf.structures()
                connections = structures[structures["Type"] == "Connection"]
                conn_names = connections["Connection"]
                for name in conn_names:
                    results.append(self._check(name, geom.hdf_path.name))
        return results


@register_check(["ffrd"], dependencies=["GeomHdfExists"])
class ReferenceLinePattern(MultiJsonSchemaChecker):
    """Checker for reference line naming conventions."""

    name = "Reference line name pattern"
    criteria = "Reference Line names should follow gage or hydro model" " reference line naming conventions."
    schema_properties = [
        "ref_line_gage",
        "ref_line_hydro_model",
    ]

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


@register_check(["ffrd"], dependencies=["GeomHdfExists"])
class ReferencePointPattern(MultiJsonSchemaChecker):
    """Checker for reference point naming conventions."""

    name = "Reference point name pattern"
    criteria = "Reference Point names should follow levee or 'other'" " reference point naming conventions."
    schema_properties = [
        "ref_point_levee",
        "ref_point_other",
    ]

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the reference point title follows the naming convention.

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
                    refpoints = geom.hdf.reference_points_names(mesh)
                    for ref_point in refpoints:
                        results.append(self._check(ref_point, geom.hdf_path.name))
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


@register_check(["ffrd"], dependencies=["SingleGeometryFile"])
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
        return RasqcResult(name=self.name, filename=geom_file.path.name, result=ResultStatus.OK)

    def run(self, ras_model: RasModel) -> List[RasqcResult]:
        """Check if the geometry file title follows the naming convention.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check.

        Returns
        -------
            RasqcResult: The result of the check.
        """
        results = [self._check(ras_model.prj_file.path.name, g) for g in ras_model.geometries]
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
