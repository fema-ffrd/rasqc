"""Naming convention checkers for FFRD HEC-RAS STAC Items."""

from ..base_checker import RasqcChecker
from ..registry import register_check
from ..result import RasqcResult, ResultStatus
from .naming import load_hms_schema, load_ras_schema, get_schema_property

from jsonschema import validate, ValidationError

import json
from typing import List
from pathlib import Path

from typing import Dict, List, Any


class StacChecker(RasqcChecker):
    """Base class for checking STAC asset fields against JSON schema."""

    schema_property: str
    check_type: str

    def __init__(self):
        if self.check_type == "hms":
            self.schema = load_hms_schema()
        else:
            self.schema = load_ras_schema()

    def _check_property(self, value: Any, filename: str) -> RasqcResult:
        property_schema = get_schema_property(self.schema, self.schema_property)
        try:
            validate(value, property_schema)
            return RasqcResult(
                name=self.name, filename=filename, result=ResultStatus.OK, message=value
            )
        except ValidationError:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.ERROR,
                message=f"'{value}': {property_schema.get('description', self.criteria)}",
                pattern=property_schema.get("pattern"),
                examples=property_schema.get("examples"),
            )

    def run(self, stac_item: Dict[str, Any]) -> List[RasqcResult]:
        """Run the check on each asset inside a single STAC item."""
        results = []
        assets = stac_item.get("assets", {})
        for asset_name, asset_props in assets.items():
            normalized_props = {
                key.split(":", 1)[-1]: val for key, val in asset_props.items()
            }
            if self.schema_property in normalized_props:
                values = normalized_props[self.schema_property]
                if not isinstance(values, list):
                    values = [values]
                for val in values:
                    if isinstance(val, str):
                        val = val.strip()
                    results.append(self._check_property(val, asset_name))
        return results


class MultiSchemaChecker(StacChecker):
    """Checker for properties where each value must match one of multiple schema keys."""

    valid_schema_keys: List[str] = []
    check_type: str

    def __init__(self):
        if self.check_type == "hms":
            self.schema = load_hms_schema()
        else:
            self.schema = load_ras_schema()

    def run(self, stac_item: Dict[str, Any]) -> List[RasqcResult]:
        """Run the check on one stac property against multiple possible schemas."""
        results = []
        assets = stac_item.get("assets", {})

        # Load schemas to try for each value
        candidate_schemas = [
            get_schema_property(self.schema, key) for key in self.valid_schema_keys
        ]

        for asset_name, asset_props in assets.items():
            normalized_props = {
                key.split(":", 1)[-1]: val for key, val in asset_props.items()
            }
            if self.schema_property not in normalized_props:
                continue

            values = normalized_props[self.schema_property]
            if not isinstance(values, list):
                values = [values]

            for val in values:
                if isinstance(val, dict):
                    val = list(val.values())[0]  # Extract value if it's a dictionary
                matched = False

                for schema in candidate_schemas:
                    try:
                        validate(val, schema)
                        matched = True
                        break
                    except ValidationError:
                        continue

                if matched:
                    results.append(
                        RasqcResult(
                            name=self.name,
                            filename=asset_name,
                            result=ResultStatus.OK,
                            message=val,
                        )
                    )
                else:
                    results.append(
                        RasqcResult(
                            name=self.name,
                            filename=asset_name,
                            result=ResultStatus.ERROR,
                            message=f"'{val}' does not match any of the expected patterns.",
                            pattern=" | ".join(
                                s.get("pattern", "") for s in candidate_schemas
                            ),
                            examples=[s.get("examples") for s in candidate_schemas],
                        )
                    )
        return results


class AssetChecker(StacChecker):
    """Checker for validating GeoJSON asset names against the naming conventions."""

    def __init__(self, geojson_file: str, property_name: str, check_type: str = "hms"):
        self.geojson_file = geojson_file
        self.property = property_name
        self.check_type = check_type

        self.name = self.__class__.name
        self.criteria = self.__class__.criteria
        if self.check_type == "hms":
            self.schema = load_hms_schema()
        else:
            self.schema = load_ras_schema()
        self.property_schema = get_schema_property(self.schema, self.property)

    def run(self) -> List[RasqcResult]:
        """Run the check on each feature in the GeoJSON file."""
        results = []
        with open(self.geojson_file) as f:
            geojson = json.load(f)
            for feature in geojson.get("features", []):
                feature_name = feature.get("properties", {}).get("name", "")
                if feature_name:
                    feature_name = feature_name.strip()
                    results.append(
                        self._check_property(feature_name, Path(self.geojson_file).name)
                    )
        return results


@register_check(["ras_stac_ffrd"])
class PrjFilenamePattern(StacChecker):
    """Checker for project filename pattern."""

    name = "Project filename pattern"
    criteria = (
        "Project filename should follow the pattern 'subbasin-name',"
        " where the subbasin name is all lowercase letters and hyphens."
    )
    schema_property = "project_file_name"
    check_type = "ras"

    def run(self, stac_item: Dict[str, Any]) -> List[RasqcResult]:
        """Run the check on item level properties."""
        results = []
        props = stac_item.get("properties", {})  # check item level properties

        if self.schema_property in props:
            val = props[self.schema_property]
            if isinstance(val, str):
                val = val.strip()
            results.append(self._check_property(val, "item"))

        return results


@register_check(["ras_stac_ffrd"])
class PlanTitleChecker(StacChecker):
    """Checker for plan name pattern."""

    name = "Plan title"
    criteria = "Plan file title should follow the naming convention 'event-type_event-name' where event type and event name are lowercase and hyphens."
    schema_property = "plan_title"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class GeometryTitlePattern(StacChecker):
    """Checker for geometry file title naming conventions."""

    name = "Geometry title"
    criteria = (
        "Geometry file title should follow the pattern 'model-unit',"
        "where the model unit is all lowercase letters and hyphens."
    )
    schema_property = "geometry_title"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class UnsteadyFlowTitlePattern(StacChecker):
    """Checker for unsteady flow file title naming conventions."""

    name = "Unsteady Flow title"
    criteria = "Unsteady Flow file title should follow the pattern 'event-name' where the event name is lowercase and hyphens."
    schema_property = "unsteady_flow_title"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class PlanShortIdPattern(StacChecker):
    """Checker for plan file short ID naming conventions."""

    name = "Plan short ID"
    criteria = "Plan file short ID should be identical to the Plan name. "
    schema_property = "plan_short_id"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class TerrainNamePattern(StacChecker):
    """Checker for terrain file naming conventions."""

    name = "Terrain name"
    criteria = "Terrain file name should follow the naming convention 'model-unit_'terrain'_resolution[_'merged']' where the model unit is lowercase and hyphens."
    schema_property = "terrain_name"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class D2FlowArea(StacChecker):
    """Checker for 2D Flow Area naming conventions."""

    name = "2D Flow Area"
    criteria = (
        "2D Flow Area names should follow the naming convention "
        "'model-unit[_integer]', where '[_integer]' is an optional suffix "
        " for multiple 2D Flow Areas in the same geometry."
    )
    schema_property = "2d_flow_element"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class PrecipBoundaryConditionPattern(StacChecker):
    """Checker for precipitation boundary condition DSS path conventions."""

    name = "Precip Boundary Condition name"
    criteria = "Precip Boundary Condition names should follow naming conventions for precipitation boundary conditions."
    schema_property = "precip_bc"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class InitialConditionPointPattern(StacChecker):
    """Checker for initial condition point naming conventions."""

    name = "Initial Condition Point name"
    criteria = "Initial Condition Point names should follow naming convention ''ic'_reservoir-name[_integer]' where the reservoir name is lowercase and hyphens."
    schema_property = "initial_condition_point_name"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class RefLinePattern(MultiSchemaChecker):
    """Checker for ref_lines values."""

    name = "Reference Line"
    criteria = "Each reference line must match either the ref_line_gage or ref_line_hydro_model naming convention."
    schema_property = "ref_lines"
    valid_schema_keys = ["ref_line_gage", "ref_line_hydro_model"]
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class RefPointPattern(MultiSchemaChecker):
    """Checker for ref_points values."""

    name = "Reference Point"
    criteria = "Each reference point must match either the ref_point_levee or ref_point_other naming convention."
    schema_property = "ref_points"
    valid_schema_keys = ["ref_point_levee", "ref_point_other"]
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class BoundaryConditionPattern(MultiSchemaChecker):
    """Checker for boundary_locations — must match one of the allowed BC schemas."""

    name = "Boundary Condition"
    criteria = "Each boundary condition must match either the inflow_bc_from_ras, outflow_bc_to_ras, internal_bc_from_hms, or outflow_bc naming convention."
    schema_property = "boundary_locations"
    valid_schema_keys = [
        "inflow_bc_from_ras",
        "outflow_bc_to_ras",
        "internal_bc_from_hms",
        "outflow_bc",
    ]
    check_type = "ras"


@register_check(["hms_stac_ffrd"])
class ProjectTitlePattern(StacChecker):
    """Checker for project title naming conventions."""

    name = "Project Title."
    criteria = (
        "Project title should follow the pattern 'basin-name [_integer]'"
        "where the subbasin name is all lowercase letters and hyphens."
    )
    schema_property = "project_title"
    check_type = "hms"


@register_check(["hms_stac_ffrd"])
class BasinTitlePattern(StacChecker):
    """Checker for basin title naming conventions."""

    name = "Basin Title."
    criteria = (
        "Basin title should follow the pattern 'basin-name_event-name'"
        "where the basin and event names are all lowercase letters and hyphens."
    )
    schema_property = "basin_title"
    check_type = "hms"


@register_check(["hms_stac_ffrd"])
class MetTitlePattern(StacChecker):
    """Checker for met title naming conventions."""

    name = "Met Title."
    criteria = "Met title should follow the pattern 'event-name' where the event name is all lowercase letters and hyphens."
    schema_property = "met_title"
    check_type = "hms"


@register_check(["hms_stac_ffrd"])
class ControlTitlePattern(StacChecker):
    """Checker for control title naming conventions."""

    name = "Control Title."
    criteria = "Control title should follow the pattern 'event-name' where the event name is all lowercase letters and hyphens."
    schema_property = "control_title"
    check_type = "hms"


@register_check(["hms_stac_ffrd"])
class RunTitlePattern(StacChecker):
    """Checker for run title naming conventions."""

    name = "Run Title."
    criteria = "Run title should follow the pattern 'basin-name' where the basin name is all lowercase letters and hyphens."
    schema_property = "run_title"
    check_type = "hms"


class SinkElementPattern(AssetChecker):
    """Checker for validating sink element names in GeoJSON files."""

    name = "Sink Element"
    criteria = "Sink elements should follow the pattern 'reference-name' where the reference name is all lowercase letters and hyphens."
    schema_property = "sink_element"
    check_type = "hms"


class JunctionElementPattern(AssetChecker):
    """Checker for validating junction element names in GeoJSON files."""

    name = "Junction Element"
    criteria = "Junction elements should follow the pattern 'reference-name[+ reference-name]_'j'unique-id' where the reference name is all lowercase letters and hyphens."
    schema_property = "junction_element"
    check_type = "hms"


class ReservoirElementPattern(AssetChecker):
    """Checker for validating reservoir element names in GeoJSON files."""

    name = "Reservoir Element"
    criteria = "Reservoir elements should follow the pattern ''nid'_nid-id[_other-structure-id]'."
    schema_property = "reservoir_element"
    check_type = "hms"


class ReachElementPattern(AssetChecker):
    """Checker for validating reach element names in GeoJSON files."""

    name = "Reach Element"
    criteria = "Reach elements should follow the pattern 'reference-name_'r'unique-id' where the reference name is all lowercase letters and hyphens."
    schema_property = "reach_element"
    check_type = "hms"


class SubbasinElementPattern(AssetChecker):
    """Checker for validating subbasin element names in GeoJSON files."""

    name = "Subbasin Element"
    criteria = "Subbasin elements should follow the pattern 'reference-name_'s'unique-id' where the reference name is all lowercase letters and hyphens."
    schema_property = "subbasin_element"
    check_type = "hms"
