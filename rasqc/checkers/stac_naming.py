"""Naming convention checkers for FFRD HEC-RAS STAC Items."""

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
from typing import List

from typing import Dict, List, Any


def _load_schema() -> dict:
    """Load the JSON schema for naming conventions."""
    with importlib.resources.path("rasqc.data", "naming-schema.json") as path:
        with open(path) as f:
            return json.load(f)


NAMING_SCHEMA = _load_schema()


def _get_schema(property_name: str) -> dict:
    """Get a property from the naming schema."""
    return NAMING_SCHEMA["properties"][property_name]


def _load_schema() -> dict:
    """Load the JSON schema for naming conventions."""
    with importlib.resources.path("rasqc.data", "naming-schema.json") as path:
        with open(path) as f:
            return json.load(f)


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
            return RasqcResult(
                name=self.name,
                filename=filename,
                result=ResultStatus.OK,
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

    def run(self, stac_assets: Dict[str, Dict[str, Any]]) -> List[RasqcResult]:
        """Run the check on each asset, stripping prefix from colon-delimited keys."""
        results = []

        for asset_name, asset_props in stac_assets.items():
            normalized_props = {key.split(":", 1)[-1]: val for key, val in asset_props.items()}

            if self.schema_property in normalized_props:
                val = normalized_props[self.schema_property]
                if isinstance(val, str):
                    val = val.strip()
                results.append(self._check_property(val, asset_name))

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


# TODO: Terrain Name


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


# TODO: BC Lines


@register_check(["stac_ffrd"])
class PrecipBoundaryConditionPattern(StacChecker):
    """Checker for precipitation boundary condition DSS path conventions."""

    name = "Precip Boundary Condition name pattern"
    criteria = "Precip Boundary Condition names should follow naming conventions for precipitation boundary conditions."
    schema_property = "precip_bc"


# TODO: IC Points
