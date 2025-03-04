from geopandas import GeoDataFrame

from dataclasses import dataclass
from enum import Enum
from json import JSONEncoder
from typing import Any, Optional, Union


class ResultStatus(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    NOTE = "note"


class RasqcResultEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, GeoDataFrame):
            return obj.to_json()
        return super().default(obj)


@dataclass
class RasqcResult:
    result: ResultStatus
    name: str
    filename: Union[str, list[str]]
    message: Optional[Union[str, dict, list[str], list[dict]]] = None
    gdf: Optional[GeoDataFrame] = None
