from pathlib import Path
import json
from rasqc.result import RasqcResultEncoder
from rasqc.main import run_json


TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagle/BaldEagleDamBrk.prj"
MUNCIE_PRJ = TEST_DATA / "ras/Muncie/Muncie.prj"


def test_run_json_a():
    res = run_json(str(BALDEAGLE_PRJ), "ble")
    del res["timestamp"]
    assert json.dumps(res, cls=RasqcResultEncoder) == json.dumps(
        {
            "model": "tests\\data\\ras\\BaldEagle\\BaldEagleDamBrk.prj",
            "checksuite": "ble",
            "checks": [
                {
                    "result": "note",
                    "name": "Geometry Projection",
                    "filename": "BaldEagleDamBrk.g11.hdf",
                    "message": "HEC-RAS geometry HDF file projection: 'NAD83 / Pennsylvania North (ftUS)'",
                    "gdf": None,
                },
                {
                    "result": "note",
                    "name": "2D Equation Set",
                    "filename": ["BaldEagleDamBrk.p13.hdf", "BaldEagleDamBrk.p18.hdf"],
                    "message": [
                        "2D Equation Set(s): '['Diffusion Wave', 'Diffusion Wave', 'Diffusion Wave']'",
                        "2D Equation Set(s): '['Diffusion Wave', 'Diffusion Wave']'",
                    ],
                    "gdf": None,
                },
            ],
        },
        cls=RasqcResultEncoder,
    )


def test_run_json_b():
    res = run_json(str(MUNCIE_PRJ), "ble")
    del res["timestamp"]
    assert json.dumps(res, cls=RasqcResultEncoder) == json.dumps(
        {
            "model": "tests\\data\\ras\\Muncie\\Muncie.prj",
            "checksuite": "ble",
            "checks": [
                {
                    "result": "note",
                    "name": "Geometry Projection",
                    "filename": "Muncie.g02.hdf",
                    "message": "HEC-RAS geometry HDF file projection: 'NAD83 / Indiana East (ftUS)'",
                    "gdf": None,
                },
                {
                    "result": "note",
                    "name": "2D Equation Set",
                    "filename": ["Muncie.p03.hdf"],
                    "message": ["2D Equation Set(s): 'Diffusion Wave'"],
                    "gdf": None,
                },
            ],
        },
        cls=RasqcResultEncoder,
    )
