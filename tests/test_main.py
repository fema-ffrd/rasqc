from pathlib import Path
from rasqc.result import ResultStatus
from rasqc.main import run_json


TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagle/BaldEagleDamBrk.prj"
MUNCIE_PRJ = TEST_DATA / "ras/Muncie/Muncie.prj"


def test_run_json_a():
    res = run_json(str(BALDEAGLE_PRJ), "ble")
    del res["timestamp"]
    res["checks"] = [res["checks"][0]]
    assert res == {
        "model": "tests\\data\\ras\\BaldEagle\\BaldEagleDamBrk.prj",
        "checksuite": "ble",
        "checks": [
            {
                "result": ResultStatus.NOTE,
                "name": "Geometry Projection",
                "filename": "BaldEagleDamBrk.g11.hdf",
                "message": "NAD83 / Pennsylvania North (ftUS)",
                "gdf": None,
            },
        ],
    }


def test_run_json_b():
    res = run_json(str(MUNCIE_PRJ), "ble")
    del res["timestamp"]
    res["checks"] = [res["checks"][0]]
    assert res == {
        "model": "tests\\data\\ras\\Muncie\\Muncie.prj",
        "checksuite": "ble",
        "checks": [
            {
                "result": ResultStatus.NOTE,
                "name": "Geometry Projection",
                "filename": "Muncie.g02.hdf",
                "message": "NAD83 / Indiana East (ftUS)",
                "gdf": None,
            },
        ],
    }
