from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.event_conditions import *
from rasqc.result import ResultStatus

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_MeteorologyPrecip():
    assert {
        res.filename: res.to_dict()
        for res in MeteorologyPrecip().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Meteorology Precipitation",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "No HDF file located.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Meteorology Precipitation",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": "No meteorology precip applied.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }


def test_PrecipHydrographs():
    assert {
        res.filename: res.to_dict()
        for res in PrecipHydrographs().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Precipitation Hydrographs",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "No HDF file located.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Precipitation Hydrographs",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": "No precip hydrograph applied.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }


def test_FlowHydrographs():
    assert {
        res.filename: res.to_dict()
        for res in FlowHydrographs().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Flow Hydrographs",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "No HDF file located.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Flow Hydrographs",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": '{"2D Flow Area": "Upper 2D Area", "BC Line": "Upstream Q", "EG Slope For Distributing Flow": 0.0010000000474974513, "Peak Flow": 22000.0}',
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }


def test_StageHydrographs():
    assert {
        res.filename: res.to_dict()
        for res in StageHydrographs().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Stage Hydrographs",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "No HDF file located.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Stage Hydrographs",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": "No stage hydrograph applied.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }


def test_NormalDepths():
    assert {
        res.filename: res.to_dict()
        for res in NormalDepths().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Normal Depths",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "No HDF file located.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Normal Depths",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": '{"2D Flow Area": "BaldEagleCr", "BC Line": "DSNormalDepth", "BC Line WS": "Multiple", "Normal Depth Slope": 0.0003000000142492354}',
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }


def test_RatingCurves():
    assert {
        res.filename: res.to_dict()
        for res in RatingCurves().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Rating Curves",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "No HDF file located.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Rating Curves",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": "No rating curve applied.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }


def test_InitialConditions():
    assert {
        res.filename: res.to_dict()
        for res in InitialConditions().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Initial Conditions",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "No HDF file located.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Initial Conditions",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": "No initial conditions applied.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }
