"""HEC-RAS model file and model classes."""

import obstore
from rashdf import RasGeomHdf, RasPlanHdf

from datetime import datetime
import os
from pathlib import Path
import re
from typing import List, Optional


def _obstore_file_exists(
    store: obstore.store.ObjectStore, path: str | os.PathLike
) -> bool:
    if path is None:
        return False
    try:
        store.head(str(path))
        return True
    except FileNotFoundError:
        return False


def _get_hdf_path(path: Path) -> Optional[Path]:
    """Get the HDF path for a given file path."""
    if path.suffix == ".prj":
        return None
    return Path(f"{path}.hdf")


class RasModelFile:
    """HEC-RAS model file class.

    Represents a single file in a HEC-RAS model (project, geometry, plan, or flow file).

    Attributes
    ----------
    path: Path to the file.
    hdf_path: Path to the associated HDF file, if applicable.
    """

    local: bool
    store: Optional[obstore.store.ObjectStore] = None
    hdf_path: Optional[Path] = None

    def __init__(
        self, path: str | os.PathLike, store: Optional[obstore.store.ObjectStore] = None
    ):
        """Instantiate a RasModelFile object by the file path.

        Parameters
        ----------
        path : str | os.Pathlike
            The absolute path to the RAS file.
        store : obstore.store.ObjectStore, optional
            The obstore file system object. If not provided, it will be created based on the path.
        """
        # local file
        if not store and os.path.exists(path):
            self.local = True
            self.store = None
            self.filename = os.path.basename(path)
            self.path = Path(path)
            self.hdf_path = _get_hdf_path(self.path)
            self.content = open(path, "r").read()

        # remote file
        else:
            self.local = False
            if store:
                self.store = store
            else:
                prefix = os.path.dirname(path)
                self.store = obstore.store.from_url(prefix)
            self.filename = os.path.basename(path)
            self.path = Path(self.filename)
            self.hdf_path = _get_hdf_path(self.path)
            self.content = (
                obstore.open_reader(self.store, self.filename)
                .readall()
                .to_bytes()
                .decode("utf-8")
                .replace("\r\n", "\n") # normalize line endings
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


def _obstore_protocol_url(
    store: obstore.store.ObjectStore, path: str | os.PathLike
) -> str:
    config: dict = store.config
    match store:
        case obstore.store.S3Store():
            bucket = config["bucket"]
            return "s3", f"s3://{bucket}/{store.prefix}/{path}"
        case obstore.store.GCSStore():
            bucket = config["bucket"]
            return "gs", f"gs://{bucket}/{store.prefix}/{path}"
        case obstore.store.AzureStore():
            container_name = config["container_name"]
            return "az", f"az://{container_name}/{store.prefix}/{path}"
        case obstore.store.HTTPStore():
            return "https", f"{store.url}/{path}"
        case obstore.store.LocalStore():
            return "file", f"file://{store.prefix}/{path}"
        case _:
            raise ValueError(
                f"Unsupported ObjectStore type: {type(store)}. Supported types are S3, GCS, Azure, HTTP, and Local."
            )


class GeomFile(RasModelFile):
    """HEC-RAS geometry file class."""

    _hdf_path: str
    hdf: Optional[RasGeomHdf] = None

    def __init__(
        self, path: str | os.PathLike, store: Optional[obstore.store.ObjectStore] = None
    ):
        """Instantiate a GeomFile object by the file path.

        Parameters
        ----------
        path : str | os.Pathlike
            The absolute path to the RAS geometry file.
        store : obstore.store.ObjectStore, optional
            The obstore file system object. If not provided, it will be created based on the path.
        """
        super().__init__(path, store)
        if store and _obstore_file_exists(self.store, self.hdf_path):
            _, url = _obstore_protocol_url(self.store, self.hdf_path)
            print(f"Opening HDF file: {url}")
            self.hdf = RasGeomHdf.open_uri(
                url,
                fsspec_kwargs={
                    "default_cache_type": "blockcache",
                    "default_block_size": 10**5,
                },
            )
        elif os.path.exists(self.hdf_path):
            self.hdf = RasGeomHdf(self.hdf_path)

    def last_updated(self) -> datetime:
        """Get the last updated date of the file.

        Returns
        -------
            str: The last updated date of the file.
        """
        matches: List[str] = re.findall(r"(?m).*Time\s*=\s*(.+)$", self.content)
        datetimes = []
        for m in matches:
            m = m.strip()
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

    def __init__(
        self, path: str | os.PathLike, store: Optional[obstore.store.ObjectStore] = None
    ):
        """Instantiate a PlanFile object by the file path.

        Parameters
        ----------
        path : str | os.Pathlike
            The absolute path to the RAS geometry file.
        store : obstore.store.ObjectStore, optional
            The obstore file system object. If not provided, it will be created based on the path.
        """
        super().__init__(path, store)
        if store and _obstore_file_exists(self.store, self.hdf_path):
            _, url = _obstore_protocol_url(self.store, self.hdf_path)
            print(f"Opening HDF file: {url}")
            self.hdf = RasPlanHdf.open_uri(
                url,
                fsspec_kwargs={
                    "default_cache_type": "blockcache",
                    "default_block_size": 10**5,
                },
            )
        elif os.path.exists(self.hdf_path):
            self.hdf = RasPlanHdf(self.hdf_path)

    @property
    def geom_file_ext(self) -> str:
        """Get the geometry file extension associated with the plan file.

        Returns
        -------
            GeomFile: The geometry file associated with the plan file.
        """
        match = re.search(r"(?m)Geom File\s*=\s*(.+)$", self.content)
        geom_ext = match.group(1)
        return geom_ext

    @property
    def flow_file_ext(self) -> str:
        """Get the unsteady flow file associated with the plan file.

        Returns
        -------
            UnsteadyFlowFile: The unsteady flow file associated with the plan file.
        """
        match = re.search(r"(?m)Flow File\s*=\s*(.+)$", self.content)
        flow_ext = match.group(1)
        return flow_ext

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

        for suf in re.findall(r"(?m)Geom File\s*=\s*(.+)$", self.prj_file.content):
            self.geom_files[suf] = GeomFile(
                self.prj_file.path.with_suffix("." + suf), self.prj_file.store
            )

        for suf in re.findall(r"(?m)Unsteady File\s*=\s*(.+)$", self.prj_file.content):
            self.unsteady_flow_files[suf] = UnsteadyFlowFile(
                self.prj_file.path.with_suffix("." + suf), self.prj_file.store
            )

        for suf in re.findall(r"(?m)Plan File\s*=\s*(.+)$", self.prj_file.content):
            self.plan_files[suf] = PlanFile(
                self.prj_file.path.with_suffix("." + suf), self.prj_file.store
            )

        current_plan_ext = re.search(
            r"(?m)Current Plan\s*=\s*(.+)$", self.prj_file.content
        )
        self.current_plan_ext = current_plan_ext.group(1) if current_plan_ext else None

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
        current_geom_ext = self.current_plan.geom_file_ext
        return self.geom_files[current_geom_ext]

    @property
    def current_unsteady(self) -> UnsteadyFlowFile:
        """Get the current unsteady flow file referenced in the current plan.

        Returns
        -------
            UnsteadyFlowFile: The current unsteady flow file.
        """
        current_unsteady_ext = self.current_plan.flow_file_ext
        return self.unsteady_flow_files[current_unsteady_ext]

    @property
    def geometries(self) -> list[GeomFile]:
        """Get all geometry files referenced in the project file.

        Returns
        -------
            list[GeomFile]: List of all geometry files.
        """
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
