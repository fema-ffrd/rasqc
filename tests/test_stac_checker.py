import pytest
from rasqc.checkers.stac_naming import InitialConditionPointPattern, PrjFilenamePattern, BasinTitlePattern
from rasqc.result import ResultStatus
import json
from pathlib import Path
from rasqc.check import asset_check

TEST_DATA = Path("./tests/data")
TEST_RAS = TEST_DATA / "stac/test_ras.json"
TEST_HMS = TEST_DATA / "stac/test_hms.json"
TEST_ASSET = TEST_DATA / "stac/hms_asset_junction.geojson"


def open_stac(test_item):
    with open(test_item) as f:
        stac_item = json.load(f)
    return stac_item


def test_prj_filename_check():
    stac_item = open_stac(TEST_RAS)
    results = PrjFilenamePattern().run(stac_item)
    result = results[0]
    assert result.name == "Project filename pattern"
    assert result.result.value == "error"


def test_initial_condition_point_check():
    stac_item = open_stac(TEST_RAS)
    result = InitialConditionPointPattern().run(stac_item)
    assert isinstance(result, list)
    assert len(result) == 17
    assert all(r.name == "Initial Condition Point name" for r in result)


def test_basin_title():
    stac_item = open_stac(TEST_HMS)
    result = BasinTitlePattern().run(stac_item)
    assert isinstance(result, list)
    assert len(result) == 6
    assert all(r.result.value == "ok" for r in result)


def test_hms_asset():
    ASSET_MAP = {
        "junction_element": TEST_ASSET,
    }
    asset_results = asset_check(ASSET_MAP)
    assert isinstance(asset_results, list)
    assert len(asset_results) == 6
    assert all(r.result.value == "error" for r in asset_results)
