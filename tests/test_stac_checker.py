import pytest
from rasqc.checkers.stac_naming import InitialConditionPointPattern, PrjFilenamePattern
from rasqc.result import ResultStatus
import json
from pathlib import Path

TEST_DATA = Path("./tests/data")
TEST_STAC = TEST_DATA / "stac/Cedar_1203_CedarCrk.json"


def open_stac():
    with open(TEST_STAC) as f:
        stac_item = json.load(f)
    return stac_item


def test_prj_filename_check():
    stac_item = open_stac()
    results = PrjFilenamePattern().run(stac_item)
    result = results[0]
    assert result.name == "Project filename pattern"
    assert result.result.value == "error"


def test_initial_condition_point_check():
    stac_item = open_stac()
    result = InitialConditionPointPattern().run(stac_item)
    assert isinstance(result, list)
    assert len(result) == 17
    assert all(r.name == "Initial Condition Point name" for r in result)
