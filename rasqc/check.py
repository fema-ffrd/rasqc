"""Module for primary check function."""

import json
from os import PathLike
from typing import Dict, List

from pystac import Item

from .checkers.stac_naming import (
    JunctionElementPattern,
    ReachElementPattern,
    ReservoirElementPattern,
    SinkElementPattern,
    SubbasinElementPattern,
)
from .checksuite import CheckSuite

# from .rasmodel import RasModel
# TODO: Lets discuss RasModel in this lib
from .registry import CHECKSUITES
from .result import RasqcResult


def check(
    ras_model: str | PathLike | Item, check_suite: str | CheckSuite
) -> List[RasqcResult]:
    """Run all checks on the provided HEC-RAS model.

    Parameters
    ----------
        ras_model: The HEC-RAS model to check.

    Returns
    -------
        List[RasqcResult]: List of results from all checks.
    """
    if isinstance(check_suite, str):
        check_suite: CheckSuite = CHECKSUITES[check_suite]

    if isinstance(ras_model, Item):
        return check_suite.run_checks(ras_model.to_dict())

    elif ras_model.endswith(".json"):
        with open(ras_model) as f:
            stac_item = json.load(f)
        return check_suite.run_checks(stac_item)

    return check_suite.run_checks(ras_model)


def asset_check(asset_map: Dict[str, str]) -> List[RasqcResult]:
    """Loop through the asset map and check each GeoJSON asset."""
    asset_results = []

    for property_name, geojson_file in asset_map.items():
        if property_name == "sink_element":
            asset_checker = SinkElementPattern(geojson_file, property_name)
        elif property_name == "junction_element":
            asset_checker = JunctionElementPattern(geojson_file, property_name)
        elif property_name == "subbasin_element":
            asset_checker = SubbasinElementPattern(geojson_file, property_name)
        elif property_name == "reservoir_element":
            asset_checker = ReservoirElementPattern(geojson_file, property_name)
        elif property_name == "reach_element":
            asset_checker = ReachElementPattern(geojson_file, property_name)
        else:
            print(f"Property name: {property_name} not a valid property.")
            continue

        asset_results.extend(asset_checker.run())

    return asset_results
