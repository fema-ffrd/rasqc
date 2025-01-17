from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.naming import PrjFileNaming, PlanTitleNaming, GeometryTitleNaming, UnsteadyFlowTitleNaming

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"

def test_PrjFileNaming():
    assert PrjFileNaming().run(RasModel(BALDEAGLE_PRJ)).message == "HEC-RAS project file 'BaldEagleDamBrk.prj' does not follow the naming convention 'Basin_Name_<HUC4-ID>_Subbasin_name.prj', where <HUC4-ID> is a 4-digit HUC number."

def test_PlanTitleNaming():
    assert PlanTitleNaming().run(RasModel(BALDEAGLE_PRJ)).message == "HEC-RAS plan file title '2D to 2D Run' does not follow the naming convention 'MonYEAR Event' (BaldEagleDamBrk.p18)"

def test_GeometryTitleNaming():
    assert GeometryTitleNaming().run(RasModel(BALDEAGLE_PRJ)).message == "HEC-RAS geometry file title '2D to 2D Connection' does not follow the naming convention 'Watershed Name FFRD' (BaldEagleDamBrk.g11)"

def test_UnsteadyFlowTitleNaming():
    assert UnsteadyFlowTitleNaming().run(RasModel(BALDEAGLE_PRJ)).message == "HEC-RAS unsteady flow file title '1972 Flood Event - 2D to 2D Run' does not follow the naming convention 'MonYEAR' (BaldEagleDamBrk.u10)"
