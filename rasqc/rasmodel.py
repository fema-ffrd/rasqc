import os
from pathlib import Path
import re


class RasModelFile:
    """HEC-RAS model file class."""

    def __init__(self, path: str | os.PathLike):
        """Instantiate a RasModelFile object by the file path.

        Parameters
        ----------
        path : str | os.Pathlike
            The absolute path to the RAS file.
        """
        self.path = Path(path)
        self.hdf_path = (
            None
            if self.path.suffix == ".prj"
            else self.path.with_suffix(self.path.suffix + ".hdf")
        )

    @property
    def title(self):
        with open(self.path, "r") as f:
            content = f.read()
            match = re.search(r"(?m)^(Proj|Geom|Plan|Flow) Title\s*=\s*(.+)$", content)
            title = match.group(2)
            return title


class RasModel:
    """HEC-RAS model class."""

    def __init__(self, prj_file: str | os.PathLike):
        """Instantiate a RasModel object by the '.prj' file path.

        Parameters
        ----------
        prj_file : str | os.Pathlike
            The absolute path to the RAS '.prj' file.
        """
        self.prj_file = RasModelFile(prj_file)
        self.title = self.prj_file.title

    @property
    def current_plan(self) -> RasModelFile:
        with open(self.prj_file.path, "r") as f:
            match = re.search(r"(?m)Current Plan\s*=\s*(.+)$", f.read())
            current_plan_ext = match.group(1)
            return RasModelFile(self.prj_file.path.with_suffix(f".{current_plan_ext}"))
        
    @property
    def current_geometry(self) -> RasModelFile:
        with open(self.current_plan.path, "r") as f:
            match = re.search(r"(?m)Geom File\s*=\s*(.+)$", f.read())
            current_geom_ext = match.group(1)
            return RasModelFile(self.prj_file.path.with_suffix(f".{current_geom_ext}"))
        
    @property
    def current_unsteady(self) -> RasModelFile:
        with open(self.current_plan.path, "r") as f:
            match = re.search(r"(?m)Flow File\s*=\s*(.+)$", f.read())
            current_flow_ext = match.group(1)
            return RasModelFile(self.prj_file.path.with_suffix(f".{current_flow_ext}"))

    @property
    def geometries(self) -> list[RasModelFile]:
        with open(self.prj_file.path, "r") as f:
            return list(
                RasModelFile(self.prj_file.path.with_suffix("." + suf))
                for suf in re.findall(r"(?m)Geom File\s*=\s*(.+)$", f.read())
            )

    @property
    def geometry_paths(self) -> list[Path]:
        return list(x.path for x in self.geometries)

    @property
    def geometry_hdf_paths(self) -> list[Path]:
        return list(x.hdf_path for x in self.geometries)

    @property
    def geometry_titles(self) -> list[str]:
        return list(x.title for x in self.geometries)

    @property
    def plans(self) -> list[RasModelFile]:
        with open(self.prj_file.path, "r") as f:
            return list(
                RasModelFile(self.prj_file.path.with_suffix("." + suf))
                for suf in re.findall(r"(?m)Plan File\s*=\s*(.+)$", f.read())
            )

    @property
    def plan_paths(self) -> list[Path]:
        return list(x.path for x in self.plans)

    @property
    def plan_hdf_paths(self) -> list[Path]:
        return list(x.hdf_path for x in self.plans)

    @property
    def plan_titles(self) -> list[str]:
        return list(x.title for x in self.plans)

    @property
    def unsteadies(self) -> list[RasModelFile]:
        with open(self.prj_file.path, "r") as f:
            return list(
                RasModelFile(self.prj_file.path.with_suffix("." + suf))
                for suf in re.findall(r"(?m)Unsteady File\s*=\s*(.+)$", f.read())
            )

    @property
    def unsteady_paths(self) -> list[Path]:
        return list(x.path for x in self.unsteadies)

    @property
    def unsteady_hdf_paths(self) -> list[Path]:
        return list(x.hdf_path for x in self.unsteadies)

    @property
    def unsteady_titles(self) -> list[str]:
        return list(x.title for x in self.unsteadies)
