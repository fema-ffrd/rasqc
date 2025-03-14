from geopandas import GeoDataFrame

from dataclasses import dataclass
from enum import Enum
from json import JSONEncoder, dumps
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
            out_dir = Path(ras_model).parent / "rasqc" / "shapes"
            out_dir.mkdir(parents=True, exist_ok=True)
            self.gdf.to_file(
                (out_dir / to_snake_case(self.name)).with_suffix(".shp"), SHPT="ARC"
            )

    def to_msg_dict(self) -> dict:
        if isinstance(self.filename, str):
            return {self.filename: self.message}
        elif isinstance(self.filename, list):
            return {n: m for n, m in zip(self.filename, self.message)}

    def to_msg_str(self) -> str:
        if self.message and isinstance(self.message, str):
            return self.filename + ": " + bold_single_quotes(self.message)
        else:
            return bold_single_quotes(
                dumps(self.to_msg_dict(), cls=RasqcResultEncoder, indent=4)
            )


def bold_single_quotes(text: str) -> str:
    # Regex to find text within single quotes
    pattern = re.compile(r"'(.*?)'")

    # Replace matches with bold tags
    formatted_text = pattern.sub(r"[bold cyan]'\1'[/bold cyan]", text)

    return formatted_text


def to_snake_case(text: str) -> str:
    text = re.sub(r"[-]", " ", text)
    text = "".join([" " + c.lower() if c.isupper() else c for c in text]).lstrip()
    return re.sub(r"\s+", "_", text)
