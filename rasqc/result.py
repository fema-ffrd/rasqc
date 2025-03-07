from geopandas import GeoDataFrame

from dataclasses import dataclass
from enum import Enum
from json import JSONEncoder
from typing import Any, Optional, Union
from datetime import datetime
from pathlib import Path
import re


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
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@dataclass
class RasqcResult:
    result: ResultStatus
    name: str
    filename: Union[str, list[str]]
    message: Optional[Union[str, dict, list[str], list[dict]]] = None
    gdf: Optional[GeoDataFrame] = None

    def gdf_to_shp(self, ras_model: str) -> None:
        if self.gdf is not None:
            out_dir = Path(ras_model).parent / "rasqc"
            out_dir.mkdir(parents=True, exist_ok=True)
            self.gdf.to_file((out_dir / to_snake_case(self.name)).with_suffix(".shp"))


def to_snake_case(text: str) -> str:
    text = re.sub(r"[-]", " ", text)
    text = ''.join([' ' + c.lower() if c.isupper() else c for c in text]).lstrip()
    return re.sub(r"\s+", "_", text)
