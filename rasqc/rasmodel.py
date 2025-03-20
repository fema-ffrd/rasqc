"""HEC-RAS model file and model classes."""

from datetime import datetime
import os
from pathlib import Path
import re


class RasModelFile:
    """HEC-RAS model file class.

    Represents a single file in a HEC-RAS model (project, geometry, plan, or flow file).

    Attributes
    ----------
        path: Path to the file.
        hdf_path: Path to the associated HDF file, if applicable.
    """

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
        """Extract the title from the RAS file.

        Returns
        -------
            str: The title of the RAS file.
        """
        with open(self.path, "r") as f:
            content = f.read()
            match = re.search(r"(?m)^(Proj|Geom|Plan|Flow) Title\s*=\s*(.+)$", content)
            title = match.group(2)
            return title


class GeomFile(RasModelFile):
    """HEC-RAS geometry file class."""

    def last_updated(self) -> datetime:
        """Get the last updated date of the file.

        Returns
        -------
            str: The last updated date of the file.
        """
        with open(self.path, "r") as f:
            content = f.read()
            matches = re.findall(r"(?m).*Time\s*=\s*(.+)$", content)
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

    @property
    def geom_file(self) -> GeomFile:
        """Get the geometry file associated with the plan file.

        Returns
        -------
            GeomFile: The geometry file associated with the plan file.
        """
        with open(self.path, "r") as f:
            content = f.read()
            match = re.search(r"(?m)Geom File\s*=\s*(.+)$", content)
            geom_ext = match.group(1)
            return GeomFile(self.path.with_suffix(f".{geom_ext}"))

    @property
    def unsteady_flow_file(self) -> UnsteadyFlowFile:
        """Get the unsteady flow file associated with the plan file.

        Returns
        -------
            UnsteadyFlowFile: The unsteady flow file associated with the plan file.
        """
        with open(self.path, "r") as f:
            content = f.read()
            match = re.search(r"(?m)Flow File\s*=\s*(.+)$", content)
            flow_ext = match.group(1)
            return UnsteadyFlowFile(self.path.with_suffix(f".{flow_ext}"))

    @property
    def short_id(self) -> str:
        """Get the short ID of the plan file.

        Returns
        -------
            str: The short ID of the plan file.
        """
        with open(self.path, "r") as f:
            content = f.read()
            match = re.search(r"(?m)Short Identifier\s*=\s*(.+)$", content)
            return match.group(1).strip()


class RasModel:
    """HEC-RAS model class.

    Represents a complete HEC-RAS model, including project, geometry, plan, and flow files.

    Attributes
    ----------
        prj_file: The project file.
        title: The title of the project.
    """

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
    def current_plan(self) -> PlanFile:
        """Get the current plan file referenced in the project file.

        Returns
        -------
            PlanFile: The current plan file.
        """
        with open(self.prj_file.path, "r") as f:
            match = re.search(r"(?m)Current Plan\s*=\s*(.+)$", f.read())
            current_plan_ext = match.group(1)
            return PlanFile(self.prj_file.path.with_suffix(f".{current_plan_ext}"))

    @property
    def current_geometry(self) -> GeomFile:
        """Get the current geometry file referenced in the current plan.

        Returns
        -------
            GeomFile: The current geometry file.
        """
        with open(self.current_plan.path, "r") as f:
            match = re.search(r"(?m)Geom File\s*=\s*(.+)$", f.read())
            current_geom_ext = match.group(1)
            return GeomFile(self.prj_file.path.with_suffix(f".{current_geom_ext}"))

    @property
    def current_unsteady(self) -> UnsteadyFlowFile:
        """Get the current unsteady flow file referenced in the current plan.

        Returns
        -------
            UnsteadyFlowFile: The current unsteady flow file.
        """
        with open(self.current_plan.path, "r") as f:
            match = re.search(r"(?m)Flow File\s*=\s*(.+)$", f.read())
            current_flow_ext = match.group(1)
            return UnsteadyFlowFile(
                self.prj_file.path.with_suffix(f".{current_flow_ext}")
            )

    @property
    def geometries(self) -> list[GeomFile]:
        """Get all geometry files referenced in the project file.

        Returns
        -------
            list[GeomFile]: List of all geometry files.
        """
        with open(self.prj_file.path, "r") as f:
            return list(
                GeomFile(self.prj_file.path.with_suffix("." + suf))
                for suf in re.findall(r"(?m)Geom File\s*=\s*(.+)$", f.read())
            )

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
        with open(self.prj_file.path, "r") as f:
            return list(
                PlanFile(self.prj_file.path.with_suffix("." + suf))
                for suf in re.findall(r"(?m)Plan File\s*=\s*(.+)$", f.read())
            )

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
        with open(self.prj_file.path, "r") as f:
            return list(
                UnsteadyFlowFile(self.prj_file.path.with_suffix("." + suf))
                for suf in re.findall(r"(?m)Unsteady File\s*=\s*(.+)$", f.read())
            )

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
