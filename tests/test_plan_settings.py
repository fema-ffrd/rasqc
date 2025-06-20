from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.result import ResultStatus
from rasqc.checkers.plan_settings import EquationSet2D, EquationSet2DNote, CompSettings

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"
MUNCIE_PRJ = TEST_DATA / "ras/Muncie.prj"


def test_EquationSet2D_a():
    results = EquationSet2D().run(RasModel(BALDEAGLE_PRJ))
    result = results[0]
    assert result.result.value == "ok"


def test_EquationSet2D_b():
    results = EquationSet2D().run(RasModel(MUNCIE_PRJ))
    result = results[0]
    assert result.result.value == "ok"


def test_EquationSet2DNote():
    assert {
        res.filename: res.to_dict()
        for res in EquationSet2DNote().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.NOTE,
            "name": "2D Equation Set",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "Plan HDF file not found.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.NOTE,
            "name": "2D Equation Set",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": '{"BaldEagleCr": "Diffusion Wave", "Upper 2D Area": "Diffusion Wave"}',
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }


def test_CompSettings():
    assert {
        res.filename: res.to_dict()
        for res in CompSettings().run(RasModel(BALDEAGLE_PRJ))
    } == {
        "BaldEagleDamBrk.p13.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Computation Settings",
            "filename": "BaldEagleDamBrk.p13.hdf",
            "element": None,
            "message": "Plan HDF file not found.",
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
        "BaldEagleDamBrk.p18.hdf": {
            "result": ResultStatus.NOTE,
            "name": "Computation Settings",
            "filename": "BaldEagleDamBrk.p18.hdf",
            "element": None,
            "message": '{"computation time step base": "20SEC", "time window": ["1999-01-01T12:00:00", "1999-01-02T00:00:00"]}',
            "pattern": None,
            "pattern_description": None,
            "examples": None,
            "gdf": None,
        },
    }
