"""HEC-RAS model file and model classes."""

import fsspec
from rashdf import RasHdf, RasGeomHdf, RasPlanHdf

from datetime import datetime
import os
from pathlib import Path
import re
from typing import Optional


def _get_fsspec_protocol(fs: fsspec.AbstractFileSystem) -> str:
    """Get the protocol of the fsspec file system."""
    if isinstance(fs.protocol, (list, tuple)):
        return fs.protocol[0]
    return fs.protocol


class RasModelFile:
    """HEC-RAS model file class.

    Represents a single file in a HEC-RAS model (project, geometry, plan, or flow file).

    Attributes
    ----------
    path: Path to the file.
    hdf_path: Path to the associated HDF file, if applicable.
    """

    fs: fsspec.AbstractFileSystem

    def __init__(self, path: str | os.PathLike, fs: Optional[fsspec.AbstractFileSystem] = None):
        """Instantiate a RasModelFile object by the file path.

        Parameters
        ----------
        path : str | os.Pathlike
            The absolute path to the RAS file.
        fs : fsspec.AbstractFileSystem, optional
            The fsspec file system object. If not provided, it will be created based on the path.
        """
        if fs:
            self.fs = fs
            self.path = Path(path)
        else:
            self.fs, _, fs_paths = fsspec.get_fs_token_paths(str(path))
            self.path = Path(fs_paths[0])
        protocol = _get_fsspec_protocol(self.fs)
        fsspec_path = f"{protocol}://{self.path}"
        with self.fs.open(fsspec_path, "r") as f:
            self.content = f.read()
        self.hdf_path = (
            None
            if self.path.suffix == ".prj"
            else self.path.with_suffix(self.path.suffix + ".hdf")
        )

    @property
    def title(self):
        """Extract the title from the RAS file.

        Returns
        -------
            str: The title of the RAS file.
        """
        match = re.search(r"(?m)^(Proj|Geom|Plan|Flow) Title\s*=\s*(.+)$", self.content)
        title = match.group(2)
        return title


def _get_hdf(path: str | os.PathLike, fs: fsspec.AbstractFileSystem) -> Optional[RasHdf]:
    """Given a Plan or Geometry path, return the corresponding HDF object."""
    hdf_path = f"{path}.hdf"
    if fs.exists(hdf_path):
        return RasHdf.open_uri(hdf_path)


class GeomFile(RasModelFile):
    """HEC-RAS geometry file class."""

    _hdf_path: str
    hdf: Optional[RasGeomHdf] = None

    def __init__(self, path: str | os.PathLike, fs: Optional[fsspec.AbstractFileSystem] = None):
        """Instantiate a GeomFile object by the file path.

        Parameters
        ----------
        path : str | os.Pathlike
            The absolute path to the RAS geometry file.
        fs : fsspec.AbstractFileSystem, optional
            The fsspec file system object. If not provided, it will be created based on the path.
        """
        super().__init__(path, fs)
        protocol = _get_fsspec_protocol(self.fs)
        self._hdf_path = f"{protocol}://{self.path}.hdf"
        if self.fs.exists(self._hdf_path):
            self.hdf = RasGeomHdf.open_uri(self._hdf_path)

    def last_updated(self) -> datetime:
        """Get the last updated date of the file.

        Returns
        -------
            str: The last updated date of the file.
        """
        matches = re.findall(r"(?m).*Time\s*=\s*(.+)$", self.content)
        datetimes = []
        for m in matches:
            try:
                dt = datetime.strptime(m, "%b/%d/%Y %H:%M:%S")
                datetimes.append(dt)
                continue
            except ValueError:
                pass
            try:
                dt = datetime.strptime(m, "%d%b%Y %H:%M:%S")
                datetimes.append(dt)
                continue
            except ValueError as e:
                raise ValueError(f"Invalid date format: {m}") from e
        return max(datetimes)


class UnsteadyFlowFile(RasModelFile):
    """HEC-RAS unsteady flow file class."""

    pass


class PlanFile(RasModelFile):
    """HEC-RAS plan file class."""

    _hdf_path: str = None
    hdf: Optional[RasPlanHdf] = None

    def __init__(self, path: str | os.PathLike, fs: Optional[fsspec.AbstractFileSystem] = None):
        """Instantiate a PlanFile object by the file path.

        Parameters
        ----------
        path : str | os.Pathlike
            The absolute path to the RAS geometry file.
        fs : fsspec.AbstractFileSystem, optional
            The fsspec file system object. If not provided, it will be created based on the path.
        """
        super().__init__(path, fs)
        protocol = _get_fsspec_protocol(self.fs)
        self._hdf_path = f"{protocol}://{self.path}.hdf"
        if self.fs.exists(self._hdf_path):
            self.hdf = RasPlanHdf.open_uri(self._hdf_path)

    @property
    def geom_file(self) -> GeomFile:
        """Get the geometry file associated with the plan file.

        Returns
        -------
            GeomFile: The geometry file associated with the plan file.
        """
        match = re.search(r"(?m)Geom File\s*=\s*(.+)$", self.content)
        geom_ext = match.group(1)
        return GeomFile(self.path.with_suffix(f".{geom_ext}"), self.fs)

    @property
    def unsteady_flow_file(self) -> UnsteadyFlowFile:
        """Get the unsteady flow file associated with the plan file.

        Returns
        -------
            UnsteadyFlowFile: The unsteady flow file associated with the plan file.
        """
        match = re.search(r"(?m)Flow File\s*=\s*(.+)$", self.content)
        flow_ext = match.group(1)
        return UnsteadyFlowFile(self.path.with_suffix(f".{flow_ext}"), self.fs)

    @property
    def short_id(self) -> str:
        """Get the short ID of the plan file.

        Returns
        -------
            str: The short ID of the plan file.
        """
        match = re.search(r"(?m)Short Identifier\s*=\s*(.+)$", self.content)
        return match.group(1).strip()


class RasModel:
    """HEC-RAS model class.

    Represents a complete HEC-RAS model, including project, geometry, plan, and flow files.

    Attributes
    ----------
        prj_file: The project file.
        title: The title of the project.
    """

    geom_files: dict[str, GeomFile]
    unsteady_flow_files: dict[str, UnsteadyFlowFile]
    plan_files: dict[str, PlanFile]
    current_plan_ext: Optional[str]

    def __init__(self, prj_file: str | os.PathLike):
        """Instantiate a RasModel object by the '.prj' file path.

        Parameters
        ----------
        prj_file : str | os.Pathlike
            The absolute path to the RAS '.prj' file.
        """
        self.prj_file = RasModelFile(prj_file)
        self.title = self.prj_file.title
        self.geom_files = {}
        self.unsteady_flow_files = {}
        self.plan_files = {}

        fs = self.prj_file.fs

        for suf in re.findall(r"(?m)Geom File\s*=\s*(.+)$", self.prj_file.content):
            self.geom_files[suf] = GeomFile(self.prj_file.path.with_suffix("." + suf), fs)

        for suf in re.findall(r"(?m)Unsteady File\s*=\s*(.+)$", self.prj_file.content):
            self.unsteady_flow_files[suf] = UnsteadyFlowFile(self.prj_file.path.with_suffix("." + suf), fs)

        for suf in re.findall(r"(?m)Plan File\s*=\s*(.+)$", self.prj_file.content):
            self.plan_files[suf] = PlanFile(self.prj_file.path.with_suffix("." + suf), fs)

        current_plan_ext = re.search(r"(?m)Current Plan\s*=\s*(.+)$", self.prj_file.content)
        self.current_plan_ext = current_plan_ext.group(1) if current_plan_ext else None


    # @property
    # def current_plan(self) -> PlanFile:
    #     """Get the current plan file referenced in the project file.

    #     Returns
    #     -------
    #         PlanFile: The current plan file.
    #     """
    #     match = re.search(r"(?m)Current Plan\s*=\s*(.+)$", self.prj_file.content)
    #     current_plan_ext = match.group(1)
    #     return PlanFile(self.prj_file.path.with_suffix(f".{current_plan_ext}"))

    @property
    def current_plan(self) -> PlanFile:
        """Get the current plan file referenced in the project file.

        Returns
        -------
            PlanFile: The current plan file.
        """
        return self.plan_files[self.current_plan_ext]

    @property
    def current_geometry(self) -> GeomFile:
        """Get the current geometry file referenced in the current plan.

        Returns
        -------
            GeomFile: The current geometry file.
        """
        # with open(self.current_plan.path, "r") as f:
        #     match = re.search(r"(?m)Geom File\s*=\s*(.+)$", f.read())
        #     current_geom_ext = match.group(1)
        #     return GeomFile(self.prj_file.path.with_suffix(f".{current_geom_ext}"))
        current_geom_ext = self.current_plan.geom_file.path.suffix
        return self.geom_files[current_geom_ext[1:]]

    @property
    def current_unsteady(self) -> UnsteadyFlowFile:
        """Get the current unsteady flow file referenced in the current plan.

        Returns
        -------
            UnsteadyFlowFile: The current unsteady flow file.
        """
        # with open(self.current_plan.path, "r") as f:
        #     match = re.search(r"(?m)Flow File\s*=\s*(.+)$", f.read())
        #     current_flow_ext = match.group(1)
        #     return UnsteadyFlowFile(
        #         self.prj_file.path.with_suffix(f".{current_flow_ext}")
        #     )
        current_unsteady_ext = self.current_plan.unsteady_flow_file.path.suffix
        return self.unsteady_flow_files[current_unsteady_ext[1:]]

    @property
    def geometries(self) -> list[GeomFile]:
        """Get all geometry files referenced in the project file.

        Returns
        -------
            list[GeomFile]: List of all geometry files.
        """
        # with open(self.prj_file.path, "r") as f:
        #     return list(
        #         GeomFile(self.prj_file.path.with_suffix("." + suf))
        #         for suf in re.findall(r"(?m)Geom File\s*=\s*(.+)$", f.read())
        #     )
        return self.geom_files.values()

    @property
    def geometry_paths(self) -> list[Path]:
        """Get paths to all geometry files.

        Returns
        -------
            list[Path]: List of paths to all geometry files.
        """
        return list(x.path for x in self.geometries)

    @property
    def geometry_hdf_paths(self) -> list[Path]:
        """Get paths to all geometry HDF files.

        Returns
        -------
            list[Path]: List of paths to all geometry HDF files.
        """
        return list(x.hdf_path for x in self.geometries)

    @property
    def geometry_titles(self) -> list[str]:
        """Get titles of all geometry files.

        Returns
        -------
            list[str]: List of titles of all geometry files.
        """
        return list(x.title for x in self.geometries)

    @property
    def plans(self) -> list[PlanFile]:
        """Get all plan files referenced in the project file.

        Returns
        -------
            list[PlanFile]: List of all plan files.
        """
        # with open(self.prj_file.path, "r") as f:
        #     return list(
        #         PlanFile(self.prj_file.path.with_suffix("." + suf))
        #         for suf in re.findall(r"(?m)Plan File\s*=\s*(.+)$", f.read())
        #     )
        return self.plan_files.values()

    @property
    def plan_paths(self) -> list[Path]:
        """Get paths to all plan files.

        Returns
        -------
            list[Path]: List of paths to all plan files.
        """
        return list(x.path for x in self.plans)

    @property
    def plan_hdf_paths(self) -> list[Path]:
        """Get paths to all plan HDF files.

        Returns
        -------
            list[Path]: List of paths to all plan HDF files.
        """
        return list(x.hdf_path for x in self.plans)

    @property
    def plan_titles(self) -> list[str]:
        """Get titles of all plan files.

        Returns
        -------
            list[str]: List of titles of all plan files.
        """
        return list(x.title for x in self.plans)

    @property
    def unsteadies(self) -> list[RasModelFile]:
        """Get all unsteady flow files referenced in the project file.

        Returns
        -------
            list[RasModelFile]: List of all unsteady flow files.
        """
        # with open(self.prj_file.path, "r") as f:
        #     return list(
        #         UnsteadyFlowFile(self.prj_file.path.with_suffix("." + suf))
        #         for suf in re.findall(r"(?m)Unsteady File\s*=\s*(.+)$", f.read())
        #     )
        return self.unsteady_flow_files.values()

    @property
    def unsteady_paths(self) -> list[Path]:
        """Get paths to all unsteady flow files.

        Returns
        -------
            list[Path]: List of paths to all unsteady flow files.
        """
        return list(x.path for x in self.unsteadies)

    @property
    def unsteady_hdf_paths(self) -> list[Path]:
        """Get paths to all unsteady flow HDF files.

        Returns
        -------
            list[Path]: List of paths to all unsteady flow HDF files.
        """
        return list(x.hdf_path for x in self.unsteadies)

    @property
    def unsteady_titles(self) -> list[str]:
        """Get titles of all unsteady flow files.

        Returns
        -------
            list[str]: List of titles of all unsteady flow files.
        """
        return list(x.title for x in self.unsteadies)
