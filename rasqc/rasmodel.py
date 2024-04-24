import os
from pathlib import Path
import re


class RasModelFile:
    """Placeholder for something more sophisticated."""

    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)

    def title(self):
        with open(self.path, "r") as f:
            content = f.read()
            match = re.search(r"(?m)^(Proj|Geom|Plan|Flow) Title\s*=\s*(.+)$", content)
            title = match.group(2)
            return title


class RasModel:
    """Placeholder for something more sophisticated."""

    def __init__(self, prj_file: str | os.PathLike):
        self.prj_file = RasModelFile(prj_file)

    def geometry_file(self) -> RasModelFile:
        return RasModelFile(self.prj_file.path.with_suffix(".g01"))

    def plan_file(self) -> RasModelFile:
        return RasModelFile(self.prj_file.path.with_suffix(".p01"))
