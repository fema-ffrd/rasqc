from dataclasses import dataclass
from enum import Enum
from json import JSONEncoder
from typing import Any, Optional


class ResultStatus(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


class RasqcResultEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


@dataclass
class RasqcResult:
    result: ResultStatus
    name: str
    filename: str
    message: Optional[str] = None
