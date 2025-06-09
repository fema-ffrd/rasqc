from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.event_conditions import *
from rasqc.result import ResultStatus

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_MeteorologyPrecip():
    assert MeteorologyPrecip().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "Meteorology Precipitation",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"p13 (PMF with Multi 2D Areas)": "No HDF file located.", "p18 (2D to 2D Run)": "No meteorology precip applied."}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }


def test_PrecipHydrographs():
    assert PrecipHydrographs().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "Precipitation Hydrographs",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"p13 (PMF with Multi 2D Areas)": "No HDF file located.", "p18 (2D to 2D Run)": "No precip hydrograph applied."}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }


def test_FlowHydrographs():
    assert FlowHydrographs().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "Flow Hydrographs",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"p13 (PMF with Multi 2D Areas)": "No HDF file located.", "p18 (2D to 2D Run)": [{"2D Flow Area": "Upper 2D Area", "BC Line": "Upstream Q", "EG Slope For Distributing Flow": 0.0010000000474974513, "Peak Flow": 22000.0}]}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }


def test_StageHydrographs():
    assert StageHydrographs().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "Stage Hydrographs",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"p13 (PMF with Multi 2D Areas)": "No HDF file located.", "p18 (2D to 2D Run)": "No stage hydrograph applied."}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }


def test_NormalDepths():
    assert NormalDepths().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "Normal Depths",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"p13 (PMF with Multi 2D Areas)": "No HDF file located.", "p18 (2D to 2D Run)": [{"2D Flow Area": "BaldEagleCr", "BC Line": "DS2NormalD", "BC Line WS": "Multiple", "Normal Depth Slope": 0.0003000000142492354}, {"2D Flow Area": "BaldEagleCr", "BC Line": "DSNormalDepth", "BC Line WS": "Multiple", "Normal Depth Slope": 0.0003000000142492354}]}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }


def test_RatingCurves():
    assert RatingCurves().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "Rating Curves",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"p13 (PMF with Multi 2D Areas)": "No HDF file located.", "p18 (2D to 2D Run)": "No rating curve applied."}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }


def test_InitialConditions():
    assert InitialConditions().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "Initial Conditions",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"p13 (PMF with Multi 2D Areas)": "No HDF file located.", "p18 (2D to 2D Run)": "No initial conditions applied."}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }
