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

from typing import Dict, List, Any

##### LOAD SCHEMA LOCALLY #####
# def _load_schema() -> dict:
#     """Load the JSON schema for naming conventions."""
#     with importlib.resources.path("rasqc.data", "naming-schema.json") as path:
#         with open(path) as f:
#             return json.load(f)


SCHEMA_URL = "https://raw.githubusercontent.com/fema-ffrd/ffrd-conventions/main/hec-ras/json-schema/schema.json"


def _load_schema() -> dict:
    with urllib.request.urlopen(SCHEMA_URL) as response:
        return json.load(response)


NAMING_SCHEMA = _load_schema()


def _get_schema(property_name: str) -> dict:
    """Get a property from the naming schema."""
    return NAMING_SCHEMA["properties"][property_name]


class StacChecker(RasqcChecker):
    """Base class for checking STAC asset fields against JSON schema."""

    schema_property: str

    def _check_property(self, value: Any, filename: str) -> RasqcResult:
        schema = _get_schema(self.schema_property)
        try:
            validate(value, schema)
            return RasqcResult(name=self.name, filename=filename, result=ResultStatus.OK, message=value)
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
            normalized_props = {key.split(":", 1)[-1]: val for key, val in asset_props.items()}

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
        candidate_schemas = [NAMING_SCHEMA["properties"][key] for key in self.valid_schema_keys]

        for asset_name, asset_props in assets.items():
            normalized_props = {key.split(":", 1)[-1]: val for key, val in asset_props.items()}

            if self.schema_property not in normalized_props:
                continue

            values = normalized_props[self.schema_property]
            if not isinstance(values, list):
                values = [values]

            for val in values:
                if isinstance(val, dict):
                    val = list(val.values())[
                        0
                    ]  # if val is a dictionary (like for boundary_locations), extract the value to validate

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
                        RasqcResult(name=self.name, filename=asset_name, result=ResultStatus.OK, message=val)
                    )
                else:
                    results.append(
                        RasqcResult(
                            name=self.name,
                            filename=asset_name,
                            result=ResultStatus.ERROR,
                            message=f"'{val}' does not match any of the expected patterns.",
                            pattern=" | ".join(s.get("pattern", "") for s in candidate_schemas),
                            examples=[s.get("examples") for s in candidate_schemas],
                        )
                    )

        return results


@register_check(["stac_ffrd"])
class PrjFilenamePattern(StacChecker):
    """Checker for project filename pattern."""

    name = "Project filename pattern"
    criteria = (
        "Project filename should follow the pattern 'subbasin-name.prj',"
        " where the subbasin name is all lowercase letters and hyphens."
    )
    schema_property = "project_file_name"

    def run(self, stac_item: Dict[str, Any]) -> List[RasqcResult]:
        results = []

        props = stac_item.get("properties", {})  # check item level properties

        if self.schema_property in props:
            val = props[self.schema_property]
            if isinstance(val, str):
                val = val.strip()
            results.append(self._check_property(val, "item"))

        return results


@register_check(["stac_ffrd"])
class PlanTitleChecker(StacChecker):
    """Checker for STAC asset plan name pattern."""

    name = "STAC Plan title pattern"
    criteria = (
        "Plan file title should follow the naming convention "
        "'hydra-event-type:YYYY-MM-DD', where 'hydra-event-type'"  # double check
        " is a lowercase description "
    )
    schema_property = "plan_title"


@register_check(["stac_ffrd"])
class GeometryTitlePattern(StacChecker):
    """Checker for geometry file title naming conventions."""

    name = "Geometry title pattern"
    criteria = (
        "Geometry file title should follow the pattern 'subbasin-name',"
        "where the subbasin name is all lowercase letters and hyphens."
    )
    schema_property = "geometry_title"


@register_check(["stac_ffrd"])
class UnsteadyFlowTitlePattern(StacChecker):
    """Checker for unsteady flow file title naming conventions."""

    name = "Unsteady Flow title pattern"
    criteria = "Unsteady Flow file title should follow the pattern 'YYYY-MM-DD'."  # double check
    schema_property = "unsteady_flow_title"


@register_check(["stac_ffrd"])
class PlanShortIdPattern(StacChecker):
    """Checker for plan file short ID naming conventions."""

    name = "Plan short ID pattern"
    criteria = (
        "Plan file short ID should follow the naming convention "
        "'hydra-event-type:YYYY-MM-DD', where 'hydra-event-type'"  # double check
        " is a lowercase description "
    )
    schema_property = "plan_short_id"


@register_check(["stac_ffrd"])
class TerrainNamePattern(StacChecker):
    """Checker for terrain file naming conventions."""

    name = "Terrain name pattern"
    criteria = (
        "Terrain file name should follow the naming convention "
        "'subbasin-name[_1]', where '[_1]' is an optional suffix "
        " for multiple terrain files in the same geometry."
    )
    schema_property = "terrain_name"


@register_check(["stac_ffrd"])
class D2FlowArea(StacChecker):
    """Checker for 2D Flow Area naming conventions."""

    name = "2D Flow Area pattern"
    criteria = (
        "2D Flow Area names should follow the naming convention "
        "'subbasin-name[_1]', where '[_1]' is an optional suffix "
        " for multiple 2D Flow Areas in the same geometry."
    )
    schema_property = "2d_flow_element"


@register_check(["stac_ffrd"])
class PrecipBoundaryConditionPattern(StacChecker):
    """Checker for precipitation boundary condition DSS path conventions."""

    name = "Precip Boundary Condition name pattern"
    criteria = "Precip Boundary Condition names should follow naming conventions for precipitation boundary conditions."
    schema_property = "precip_bc"


@register_check(["stac_ffrd"])
class InitialConditionPointPattern(StacChecker):
    """Checker for initial condition point naming conventions."""

    name = "Initial Condition Point name pattern"
    criteria = "Initial Condition Point names should follow naming conventions for initial condition points."
    schema_property = "initial_condition_point_name"


@register_check(["stac_ffrd"])
class RefLinePattern(MultiSchemaChecker):
    """Checker for ref_lines values."""

    name = "Reference Line pattern"
    criteria = "Each reference line must match a known ref_line pattern."
    schema_property = "ref_lines"
    valid_schema_keys = ["ref_line_gage", "ref_line_hydro_model"]


@register_check(["stac_ffrd"])
class RefPointPattern(MultiSchemaChecker):
    """Checker for ref_points values."""

    name = "Reference Point pattern"
    criteria = "Each reference point must match a known ref_point pattern."
    schema_property = "ref_points"
    valid_schema_keys = ["ref_point_levee", "ref_point_other"]


@register_check(["stac_ffrd"])
class BoundaryConditionPattern(MultiSchemaChecker):
    """Checker for boundary_locations — must match one of the allowed BC schemas."""

    name = "Boundary Condition pattern"
    criteria = "Each boundary condition must match at least one valid naming convention."
    schema_property = "boundary_locations"
    valid_schema_keys = ["inflow_bc_from_ras", "outflow_bc_to_ras", "internal_bc_from_hms", "outflow_bc"]
