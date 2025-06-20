from pathlib import Path
from rasqc.rasmodel import RasModel
from rasqc.checkers.short_cell_faces import ShortCellFaces

TEST_DATA = Path("./tests/data")
BALDEAGLE_PRJ = TEST_DATA / "ras/BaldEagleDamBrk.prj"


def test_ShortCellFaces():
    assert (
        ShortCellFaces().run(RasModel(BALDEAGLE_PRJ)).message
        == "1 short cell faces found"
    )
