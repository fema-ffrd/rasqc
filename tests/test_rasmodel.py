from pathlib import Path
from rasqc.rasmodel import RasModel, RasModelFile

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_RasModelFile():
    rmf = RasModelFile(BALDEAGLE_PRJ)
    assert rmf.path == BALDEAGLE_PRJ.absolute()
    assert rmf.hdf_path == None
    assert rmf.title == "Bald Eagle Creek Example Dam Break Study"


def test_RasModel():
    rmf = RasModel(BALDEAGLE_PRJ)
    assert rmf.prj_file.path == RasModelFile(BALDEAGLE_PRJ).path
    assert rmf.title == "Bald Eagle Creek Example Dam Break Study"
    print(rmf.current_plan)
    assert rmf.current_plan.path.suffix == ".p18"
    assert rmf.geometry_paths == [
        BALDEAGLE_PRJ.with_suffix(".g06").absolute(),
        BALDEAGLE_PRJ.with_suffix(".g11").absolute(),
    ]
    assert rmf.geometry_hdf_paths == [
        BALDEAGLE_PRJ.with_suffix(".g06.hdf").absolute(),
        BALDEAGLE_PRJ.with_suffix(".g11.hdf").absolute(),
    ]
    assert rmf.geometry_titles == ["Bald Eagle Multi 2D Areas", "2D to 2D Connection"]
    assert rmf.plan_paths == [
        BALDEAGLE_PRJ.with_suffix(".p13").absolute(),
        BALDEAGLE_PRJ.with_suffix(".p18").absolute(),
    ]
    assert rmf.plan_hdf_paths == [
        BALDEAGLE_PRJ.with_suffix(".p13.hdf").absolute(),
        BALDEAGLE_PRJ.with_suffix(".p18.hdf").absolute(),
    ]
    assert rmf.plan_titles == ["PMF with Multi 2D Areas", "2D to 2D Run"]
    assert rmf.unsteady_paths == [
        BALDEAGLE_PRJ.with_suffix(".u07").absolute(),
        BALDEAGLE_PRJ.with_suffix(".u10").absolute(),
    ]
    assert rmf.unsteady_hdf_paths == [
        BALDEAGLE_PRJ.with_suffix(".u07.hdf").absolute(),
        BALDEAGLE_PRJ.with_suffix(".u10.hdf").absolute(),
    ]
    assert rmf.unsteady_titles == [
        "PMF with Multi 2D Areas",
        "1972 Flood Event - 2D to 2D Run",
    ]
    assert rmf.current_geometry.path.name == "BaldEagleDamBrk.g11"
    assert rmf.current_unsteady.path.name == "BaldEagleDamBrk.u10"
