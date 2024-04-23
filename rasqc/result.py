from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ResultStatus(Enum):
    OK = 1
    WARNING = 2
    ERROR = 3


@dataclass
class RasqcResult:
    result: ResultStatus
    name: str
    message: Optional[str] = None
