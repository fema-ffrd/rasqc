from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.plan_settings import EquationSet2D

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
    assert asdict(EquationSet2DNote().run(RasModel(BALDEAGLE_PRJ))) == {
        "result": ResultStatus.NOTE,
        "name": "2D Equation Set",
        "filename": ["BaldEagleDamBrk.p13.hdf", "BaldEagleDamBrk.p18.hdf"],
        "message": [
            {
                "193": "Diffusion Wave",
                "194": "Diffusion Wave",
                "LockHaven": "Diffusion Wave",
            },
            {"BaldEagleCr": "Diffusion Wave", "Upper 2D Area": "Diffusion Wave"},
        ],
        "gdf": None,
    }


def test_CompSettings():
    assert asdict(CompSettings().run(RasModel(BALDEAGLE_PRJ))) == {
        "result": ResultStatus.NOTE,
        "name": "Computation Settings",
        "filename": ["BaldEagleDamBrk.p13.hdf", "BaldEagleDamBrk.p18.hdf"],
        "message": [
            {
                "Computation Time Step Base".lower(): "30SEC",
                "Time Window".lower(): [
                    datetime(1999, 1, 1, 12, 0),
                    datetime(1999, 1, 2, 0, 0),
                ],
            },
            {
                "Computation Time Step Base".lower(): "20SEC",
                "Time Window".lower(): [
                    datetime(1999, 1, 1, 12, 0),
                    datetime(1999, 1, 2, 0, 0),
                ],
            },
        ],
        "gdf": None,
    }
