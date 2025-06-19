from pathlib import Path
from rasqc.rasmodel import RasModel, RasModelFile
import re

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_RasModelFile():
    rmf = RasModelFile(BALDEAGLE_PRJ)
    assert rmf.path == BALDEAGLE_PRJ
    assert rmf.hdf_path == None
    assert rmf.title == "Bald Eagle Creek Example Dam Break Study"
    assert re.sub(r"\s+", "", rmf.description) == re.sub(
        r"\s+",
        "",
        r"""The United States Army Corps of Engineers has granted access to the information in this model for instructional purposes only.  Do not copy, forward, or release the information without United States Army Corps of Engineers approval.  The results of this model do not deppict the data and final results from an official Corps of engineers study of this area.  These models have been develped for demonstration purposes only. This model is not a detailed model of this area.  The examples in this data set are put together to show the various ways you can link 1D and 2D elements.  The 2D areas are not detailed models (i.e. not a lot of time was spent laying out breaklines and testing cell size, time step, etc...  So this is not meant to be an example of best practices for modeling, just an example of all the different ways you can use 1D and 2D elements to model a system like this.""",
    )


def test_RasModel():
    rmf = RasModel(BALDEAGLE_PRJ)
    assert rmf.prj_file.path == RasModelFile(BALDEAGLE_PRJ).path
    assert rmf.title == "Bald Eagle Creek Example Dam Break Study"
    print(rmf.current_plan)
    assert rmf.current_plan.path.suffix == ".p18"
    assert rmf.geometry_paths == [
        BALDEAGLE_PRJ.with_suffix(".g06"),
        BALDEAGLE_PRJ.with_suffix(".g11"),
    ]
    assert rmf.geometry_hdf_paths == [
        BALDEAGLE_PRJ.with_suffix(".g06.hdf"),
        BALDEAGLE_PRJ.with_suffix(".g11.hdf"),
    ]
    assert rmf.geometry_titles == ["Bald Eagle Multi 2D Areas", "2D to 2D Connection"]
    assert rmf.plan_paths == [
        BALDEAGLE_PRJ.with_suffix(".p13"),
        BALDEAGLE_PRJ.with_suffix(".p18"),
    ]
    assert rmf.plan_hdf_paths == [
        BALDEAGLE_PRJ.with_suffix(".p13.hdf"),
        BALDEAGLE_PRJ.with_suffix(".p18.hdf"),
    ]
    assert rmf.plan_titles == ["PMF with Multi 2D Areas", "2D to 2D Run"]
    assert rmf.unsteady_paths == [
        BALDEAGLE_PRJ.with_suffix(".u07"),
        BALDEAGLE_PRJ.with_suffix(".u10"),
    ]
    assert rmf.unsteady_hdf_paths == [
        BALDEAGLE_PRJ.with_suffix(".u07.hdf"),
        BALDEAGLE_PRJ.with_suffix(".u10.hdf"),
    ]
    assert rmf.unsteady_titles == [
        "PMF with Multi 2D Areas",
        "1972 Flood Event - 2D to 2D Run",
    ]
    assert rmf.current_geometry.path.name == "BaldEagleDamBrk.g11"
    assert rmf.current_unsteady.path.name == "BaldEagleDamBrk.u10"
