"""Naming convention checkers for FFRD HEC-RAS STAC Items."""

import urllib.request
from ..base_checker import RasqcChecker
from ..registry import register_check
from ..rasmodel import RasModel, RasModelFile
from ..result import RasqcResult, ResultStatus

from jsonschema import validate, ValidationError
from geopandas import GeoDataFrame
from rashdf.utils import convert_ras_hdf_string

from datetime import date
import importlib.resources
import json
import urllib
from typing import List
from pathlib import Path

from typing import Dict, List, Any


#### LOAD SCHEMA LOCALLY #####
# def _load_schema() -> dict:
#     """Load the JSON schema for naming conventions."""
#     with importlib.resources.path("rasqc.data", "naming-schema.json") as path:
#         with open(path) as f:
#             return json.load(f)


# SCHEMA_URL = "https://raw.githubusercontent.com/fema-ffrd/ffrd-conventions/main/hec-ras/json-schema/schema.json"


# def _load_schema() -> dict:
#     with urllib.request.urlopen(SCHEMA_URL) as response:
#         return json.load(response)


# NAMING_SCHEMA = _load_schema()


# def _get_schema(property_name: str) -> dict:
#     """Get a property from the naming schema."""
#     return NAMING_SCHEMA["properties"][property_name]


def load_schema_for_check(check_type: str) -> dict:
    """Load the schema based on the check type."""
    if check_type == "hms":
        # Load the HMS-specific schema
        with importlib.resources.path("rasqc.data", "hms-naming-schema.json") as path:
            with open(path) as f:
                return json.load(f)
    # Default schema loading logic
    with importlib.resources.path("rasqc.data", "naming-schema.json") as path:
        with open(path) as f:
            return json.load(f)


def get_schema(property_name: str, check_type: str) -> dict:
    """Get a property from the loaded naming schema."""
    schema = load_schema_for_check(check_type)
    return schema["properties"][property_name]


class StacChecker(RasqcChecker):
    """Base class for checking STAC asset fields against JSON schema."""

    schema_property: str
    check_type: str = "ras"  # Default schema type

    def _check_property(self, value: Any, filename: str) -> RasqcResult:
        schema = get_schema(self.schema_property, self.check_type)
        try:
            validate(value, schema)
            return RasqcResult(
                name=self.name, filename=filename, result=ResultStatus.OK, message=value
            )
        except ValidationError:
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.ERROR,
                message=f"'{value}': {schema.get('description', self.criteria)}",
                pattern=schema.get("pattern"),
                examples=schema.get("examples"),
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

    def run(self, stac_item: Dict[str, Any]) -> List[RasqcResult]:
        results = []
        assets = stac_item.get("assets", {})

        # Load schemas to try for each value
        candidate_schemas = [
            get_schema(key, self.check_type) for key in self.valid_schema_keys
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
        self.schema_property = property_name
        self.check_type = check_type

        self.name = self.__class__.name
        self.criteria = self.__class__.criteria

        self.schema = get_schema(property_name, check_type)

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
        "Project filename should follow the pattern 'subbasin-name.prj',"
        " where the subbasin name is all lowercase letters and hyphens."
    )
    schema_property = "project_file_name"
    check_type = "ras"

    def run(self, stac_item: Dict[str, Any]) -> List[RasqcResult]:
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
    criteria = (
        "Plan file title should follow the naming convention "
        "'hydra-event-type:YYYY-MM-DD', where 'hydra-event-type'"  # double check
        " is a lowercase description "
    )
    schema_property = "plan_title"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class GeometryTitlePattern(StacChecker):
    """Checker for geometry file title naming conventions."""

    name = "Geometry title"
    criteria = (
        "Geometry file title should follow the pattern 'subbasin-name',"
        "where the subbasin name is all lowercase letters and hyphens."
    )
    schema_property = "geometry_title"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class UnsteadyFlowTitlePattern(StacChecker):
    """Checker for unsteady flow file title naming conventions."""

    name = "Unsteady Flow title"
    criteria = "Unsteady Flow file title should follow the pattern 'YYYY-MM-DD'."  # double check
    schema_property = "unsteady_flow_title"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class PlanShortIdPattern(StacChecker):
    """Checker for plan file short ID naming conventions."""

    name = "Plan short ID"
    criteria = (
        "Plan file short ID should follow the naming convention "
        "'hydra-event-type:YYYY-MM-DD', where 'hydra-event-type'"  # double check
        " is a lowercase description "
    )
    schema_property = "plan_short_id"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class TerrainNamePattern(StacChecker):
    """Checker for terrain file naming conventions."""

    name = "Terrain name"
    criteria = (
        "Terrain file name should follow the naming convention "
        "'subbasin-name[_1]', where '[_1]' is an optional suffix "
        " for multiple terrain files in the same geometry."
    )
    schema_property = "terrain_name"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class D2FlowArea(StacChecker):
    """Checker for 2D Flow Area naming conventions."""

    name = "2D Flow Area"
    criteria = (
        "2D Flow Area names should follow the naming convention "
        "'subbasin-name[_1]', where '[_1]' is an optional suffix "
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
    criteria = "Initial Condition Point names should follow naming conventions for initial condition points."
    schema_property = "initial_condition_point_name"
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class RefLinePattern(MultiSchemaChecker):
    """Checker for ref_lines values."""

    name = "Reference Line"
    criteria = "Each reference line must match a known ref_line pattern."
    schema_property = "ref_lines"
    valid_schema_keys = ["ref_line_gage", "ref_line_hydro_model"]
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class RefPointPattern(MultiSchemaChecker):
    """Checker for ref_points values."""

    name = "Reference Point"
    criteria = "Each reference point must match a known ref_point pattern."
    schema_property = "ref_points"
    valid_schema_keys = ["ref_point_levee", "ref_point_other"]
    check_type = "ras"


@register_check(["ras_stac_ffrd"])
class BoundaryConditionPattern(MultiSchemaChecker):
    """Checker for boundary_locations — must match one of the allowed BC schemas."""

    name = "Boundary Condition"
    criteria = (
        "Each boundary condition must match at least one valid naming convention."
    )
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
    name = "Project Title."
    criteria = ""
    schema_property = "project_title"
    check_type = "hms"


@register_check(["hms_stac_ffrd"])
class BasinTitlePattern(StacChecker):
    name = "Basin Title."
    criteria = ""
    schema_property = "basin_title"
    check_type = "hms"


@register_check(["hms_stac_ffrd"])
class MetTitlePattern(StacChecker):
    name = "Met Title."
    criteria = ""
    schema_property = "met_title"
    check_type = "hms"


@register_check(["hms_stac_ffrd"])
class ControlTitlePattern(StacChecker):
    name = "Control Title."
    criteria = ""
    schema_property = "control_title"
    check_type = "hms"


@register_check(["hms_stac_ffrd"])
class RunTitlePattern(StacChecker):
    name = "Run Title."
    criteria = ""
    schema_property = "run_title"
    check_type = "hms"


class SinkElementPattern(AssetChecker):
    """Checker for validating sink element names in GeoJSON files."""

    name = "Sink Element"
    criteria = "Sink element names should follow the defined pattern."
    schema_property = "sink_element"
    check_type = "hms"


class JunctionElementPattern(AssetChecker):
    """Checker for validating junction element names in GeoJSON files."""

    name = "Junction Element"
    criteria = "Junction element names should follow the defined pattern."
    schema_property = "junction_element"
    check_type = "hms"


class ReservoirElementPattern(AssetChecker):
    """Checker for validating reservoir element names in GeoJSON files."""

    name = "Reservoir Element"
    criteria = "Reservoir element names should follow the defined pattern."
    schema_property = "reservoir_element"
    check_type = "hms"


class ReachElementPattern(AssetChecker):
    """Checker for validating reach element names in GeoJSON files."""

    name = "Reach Element"
    criteria = "Reach element names should follow the defined pattern."
    schema_property = "reach_element"
    check_type = "hms"


class SubbasinElementPattern(AssetChecker):
    """Checker for validating subbasin element names in GeoJSON files."""

    name = "Subbasin Element"
    criteria = "Subbasin element names should follow the defined pattern."
    schema_property = "subbasin_element"
    check_type = "hms"
