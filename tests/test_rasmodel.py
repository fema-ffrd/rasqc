from pathlib import Path
from rasqc.rasmodel import RasModel, RasModelFile

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"

def test_RasModelFile():
    rmf = RasModelFile(BALDEAGLE_PRJ)
    assert rmf.path == BALDEAGLE_PRJ
    assert rmf.hdf_path == None
    assert rmf.title == "Bald Eagle Creek Example Dam Break Study"

def test_RasModel():
    rmf = RasModel(BALDEAGLE_PRJ)
    assert rmf.prj_file.path == RasModelFile(BALDEAGLE_PRJ).path
    assert rmf.title == "Bald Eagle Creek Example Dam Break Study"
    assert rmf.current_plan.path == RasModelFile(BALDEAGLE_PRJ.with_suffix(".p18")).path
    assert rmf.geometry_paths == [
        BALDEAGLE_PRJ.with_suffix(".g06"),
        BALDEAGLE_PRJ.with_suffix(".g11")
    ]
    assert rmf.geometry_hdf_paths == [
        BALDEAGLE_PRJ.with_suffix(".g06.hdf"),
        BALDEAGLE_PRJ.with_suffix(".g11.hdf")
    ]
    assert rmf.geometry_titles == [
        "Bald Eagle Multi 2D Areas",
        "2D to 2D Connection"
    ]
    assert rmf.plan_paths == [
        BALDEAGLE_PRJ.with_suffix(".p13"),
        BALDEAGLE_PRJ.with_suffix(".p18")
    ]
    assert rmf.plan_hdf_paths == [
        BALDEAGLE_PRJ.with_suffix(".p13.hdf"),
        BALDEAGLE_PRJ.with_suffix(".p18.hdf")
    ]
    assert rmf.plan_titles == [
        "PMF with Multi 2D Areas",
        "2D to 2D Run"
    ]
    assert rmf.unsteady_paths == [
        BALDEAGLE_PRJ.with_suffix(".u07"),
        BALDEAGLE_PRJ.with_suffix(".u10")
    ]
    assert rmf.unsteady_hdf_paths == [
        BALDEAGLE_PRJ.with_suffix(".u07.hdf"),
        BALDEAGLE_PRJ.with_suffix(".u10.hdf")
    ]
    assert rmf.unsteady_titles == [
        "PMF with Multi 2D Areas",
        "1972 Flood Event - 2D to 2D Run"
    ]
