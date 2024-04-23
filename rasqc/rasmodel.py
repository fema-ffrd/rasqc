import os
from pathlib import Path


class RasModel:
    """Placeholder for something more sophisticated."""

    def __init__(self, prj_file: str | os.PathLike):
        self.prj_file = Path(prj_file)
