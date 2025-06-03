"""Module for defining the RasqcResult class and related functionality."""

from geopandas import GeoDataFrame

from dataclasses import dataclass, asdict
from enum import Enum
from json import JSONEncoder
from typing import Any, List, Optional
from datetime import datetime


class ResultStatus(Enum):
    """Enumeration of possible check result statuses.

    Attributes
    ----------
        OK: Check passed successfully.
        WARNING: Check passed with warnings.
        ERROR: Check failed.
        NOTE: Note for informational purposes.
    """

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    NOTE = "note"


class RasqcResultEncoder(JSONEncoder):
    """JSON encoder for RasqcResult objects.

    Handles serialization of Enum values and GeoDataFrames.
    """

    def default(self, obj: Any) -> Any:
        """Convert objects to JSON serializable types.

        Parameters
        ----------
            obj: The object to serialize.

        Returns
        -------
            A JSON serializable representation of the object.
        """
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, GeoDataFrame):
            return obj.to_json()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@dataclass
class RasqcResult:
    """Result of a quality control check on a HEC-RAS model.

    Attributes
    ----------
        result: The status of the check (OK, WARNING, ERROR).
        name: The name of the check.
        filename: The filename of the checked file.
        element: Optional identifier for the specific element checked.
        message: Optional message providing details about the check result.
        pattern: Optional regular expression related to the check.
        pattern_description: Optional human-readable description of the pattern.
        examples: Optional string or list of strings containing valid examples related to the check.
        gdf: Optional GeoDataFrame containing spatial data related to the check.
    """

    result: ResultStatus
    name: str
    filename: str
    element: Optional[str] | Optional[List[str]] = None
    message: Optional[str] = None
    pattern: Optional[str] | Optional[List[str]] = None
    pattern_description: Optional[str] | Optional[List[str]] = None
    examples: Optional[str] | Optional[List[str]] = None
    gdf: Optional[GeoDataFrame] = None

    def to_dict(self) -> dict:
        """Convert RasqcResult object to dictionary.

        Returns
        -------
            dict: A dictionary representation of the object.
        """
        # encode and decode to serialize message if valid JSON
        return asdict(self)
