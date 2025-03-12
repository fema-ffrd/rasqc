from pathlib import Path
from dataclasses import asdict
from rasqc.rasmodel import RasModel
from rasqc.checkers.plan_settings import EquationSet2D, EquationSet2DNote, CompSettings
from rasqc.result import ResultStatus
from datetime import datetime


TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagle/BaldEagleDamBrk.prj"
MUNCIE_PRJ = TEST_DATA / "ras/Muncie/Muncie.prj"


def test_EquationSet2D_a():
    assert (
        EquationSet2D().run(RasModel(BALDEAGLE_PRJ)).__dict__.__str__()
        == "{'result': <ResultStatus.OK: 'ok'>, 'name': '2D Equation Set', 'filename': 'BaldEagleDamBrk.p18.hdf', 'message': None, 'gdf': None}"
    )


def test_EquationSet2D_b():
    assert (
        EquationSet2D().run(RasModel(MUNCIE_PRJ)).__dict__.__str__()
        == "{'result': <ResultStatus.OK: 'ok'>, 'name': '2D Equation Set', 'filename': 'Muncie.p03.hdf', 'message': None, 'gdf': None}"
    )


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
