from pathlib import Path
import json
from dataclasses import asdict
from rasqc.rasmodel import RasModel
from rasqc.checkers.plan_settings import EquationSet2D, EquationSet2DNote, CompSettings
from rasqc.result import RasqcResultEncoder, ResultStatus


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
    assert (
        json.dumps(
            asdict(EquationSet2DNote().run(RasModel(BALDEAGLE_PRJ))),
            cls=RasqcResultEncoder,
        )
        == '{"result": "note", "name": "2D Equation Set", "filename": ["BaldEagleDamBrk.p13.hdf", "BaldEagleDamBrk.p18.hdf"], "message": ["2D Equation Set(s): \'[\'Diffusion Wave\', \'Diffusion Wave\', \'Diffusion Wave\']\'", "2D Equation Set(s): \'[\'Diffusion Wave\', \'Diffusion Wave\']\'"], "gdf": null}'
    )


def test_CompSettings():
    assert asdict(CompSettings().run(RasModel(BALDEAGLE_PRJ))) == {
        "result": ResultStatus.NOTE,
        "name": "Computational Timestep Settings",
        "filename": ["BaldEagleDamBrk.p13.hdf", "BaldEagleDamBrk.p18.hdf"],
        "message": [
            {"Computation Time Step Base": "30SEC"},
            {"Computation Time Step Base": "20SEC"},
        ],
        "gdf": None,
    }
