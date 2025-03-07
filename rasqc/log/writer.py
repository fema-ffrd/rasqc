from jinja2 import Environment, FileSystemLoader
from enum import Enum
from pathlib import Path
import subprocess
from json import dumps

from rasqc.result import RasqcResultEncoder, RasqcResult, to_snake_case
from rasqc.rasmodel import RasModel


class ColorTheme(Enum):
    NINETIES = {
        "background": "rgb(50, 50, 50)",
        "heading1": "rgb(13, 162, 149)",
        "heading2": "rgb(150, 111, 255)",
        "body": "rgb(170, 170, 170)",
        "shadow": "rgb(100, 100, 100)",
    }


def to_file(
    model_path: str,
    checksuite: str,
    checks: list[RasqcResult],
    tool_version: str = "version 1.0",
    theme: ColorTheme = ColorTheme.NINETIES,
) -> Path:
    out_dir = Path(model_path).parent / "rasqc"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = (
        out_dir / f"rasqc_{to_snake_case(RasModel(model_path).prj_file.title)}"
    ).with_suffix(".html")
    env = Environment(loader=FileSystemLoader(Path(__file__).parent.resolve()))
    env.globals.update(
        isinstance=isinstance,
        str=str,
        list=list,
        enumerate=enumerate,
        dumps=dumps,
        RasqcResultEncoder=RasqcResultEncoder,
    )
    template = env.get_template("template.html")
    details = (
        subprocess.check_output(["echo", "%USERNAME%", "%DATE%", "%TIME%"], shell=True)
        .decode()
        .split()
    )
    subs = {
        "model_path": model_path,
        "checksuite": checksuite,
        "checks": checks,
        "tool_version": tool_version,
        "username": details[0],
        "day_name": details[1],
        "date": details[2],
        "time": details[3][:5],
        **theme.value,
    }
    with open(log_path, mode="w", encoding="utf-8") as log_file:
        log_file.write(template.render(subs))
    return log_path
