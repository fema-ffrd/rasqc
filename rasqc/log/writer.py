from jinja2 import Environment
from enum import Enum
from pathlib import Path
import subprocess
from typing import Literal

from rasqc.result import RasqcResult
from rasqc.rasmodel import RasModel


class ColorTheme(Enum):
    NINETIES = {
        "background":"rgb(50, 50, 50)",
        "heading1":"rgb(13, 162, 149)",
        "heading2":"rgb(150, 111, 255)",
        "body":"rgb(170, 170, 170)",
        "shadow":"rgb(100, 100, 100)",
    }


def to_file(
    model_path: str,
    checksuite: str,
    checks: list[RasqcResult],
    theme: ColorTheme = ColorTheme.NINETIES
) -> Path:
    out_dir = Path(model_path).parent / "rasqc"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = (out_dir / f"rasqc_{RasModel(model_path).prj_file.title}").with_suffix(".html")
    template = Environment().get_template(Path(__file__).parent.resolve() / "template.html")
    details = subprocess.check_output(["echo", "%USERNAME%", "%DATE%", "%TIME%"], shell=True).decode().split()
    subs = {
        "model_path":model_path,
        "checksuite":checksuite,
        "checks":checks,
        "username":details[0],
        "day_name": details[1],
        "date": details[2],
        "time": details[3][:5],
        **theme.value,
    }
    with open(log_path, mode="w", encoding="utf-8") as log_file:
        log_file.write(template.render(subs))
