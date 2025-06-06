from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.file_structure import FileStructure
from rasqc.result import ResultStatus

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_FileStructure():
    assert FileStructure().run(RasModel(BALDEAGLE_PRJ)).to_dict() == {
        "result": ResultStatus.NOTE,
        "name": "File Structure",
        "filename": "BaldEagleDamBrk.prj",
        "element": None,
        "message": '{"filename": "BaldEagleDamBrk.prj", "title": "Bald Eagle Creek Example Dam Break Study", "description": "The United States Army Corps of Engineers has granted access to the information in this model for instructional purposes only.  Do not copy, forward, or release the information without United States Army Corps of Engineers approval.  The results of this model do not deppict the data and final results from an official Corps of engineers study of this area.  These models have been develped for demonstration purposes only.\\n\\nThis model is not a detailed model of this area.  The examples in this data set are put together to show the various ways you can link 1D and 2D elements.  The 2D areas are not detailed models (i.e. not a lot of time was spent laying out breaklines and testing cell size, time step, etc...  So this is not meant to be an example of best practices for modeling, just an example of all the different ways you can use 1D and 2D elements to model a system like this.", "plans": {"p13": {"filename": "BaldEagleDamBrk.p13", "title": "PMF with Multi 2D Areas", "short id": "PMF Multi 2D", "description": "Predominatntly a 1D model with multiple 2D areas.  One 2D area represents the area behind a levee system.  The other 2D areas are used to model tributaries.", "geometry": {"filename": "BaldEagleDamBrk.g06", "title": "Bald Eagle Multi 2D Areas", "description": "Foster Joseph Sayers Dam and Reservoir"}, "unsteady": {"filename": "BaldEagleDamBrk.u07", "title": "PMF with Multi 2D Areas", "description": ""}}, "p18": {"filename": "BaldEagleDamBrk.p18", "title": "2D to 2D Run", "short id": "2D to 2D Run", "description": "This is an example of how to connect one 2D flow area to another 2D flow area with a hydraulic structure.  The upstream 2D flow area is used to model the reservoir pool.  The downstream 2D flow area is used to model the system below the dam.  An SA/2D Connection is used to mode the dam, including the overflow spillway and low flow gates.", "geometry": {"filename": "BaldEagleDamBrk.g11", "title": "2D to 2D Connection", "description": ""}, "unsteady": {"filename": "BaldEagleDamBrk.u10", "title": "1972 Flood Event - 2D to 2D Run", "description": ""}}}}',
        "pattern": None,
        "pattern_description": None,
        "examples": None,
        "gdf": None,
    }
