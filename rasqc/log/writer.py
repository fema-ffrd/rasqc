from jinja2 import Environment, FileSystemLoader
from enum import Enum
from pathlib import Path
import subprocess
from bs4 import BeautifulSoup

from rasqc.result import RasqcResult, to_snake_case
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
    tool_version: str = "",
    theme: ColorTheme = ColorTheme.NINETIES,
) -> Path:
    out_dir = Path(model_path).parent / "rasqc"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = (
        out_dir / f"log_rasqc_{to_snake_case(RasModel(model_path).prj_file.title)}"
    ).with_suffix(".html")
    env = Environment(loader=FileSystemLoader(Path(__file__).parent.resolve()))
    env.globals.update(res_dict_to_html_table=res_dict_to_html_table)
    template = env.get_template("template.html")
    details = (
        subprocess.check_output(["echo", "%USERNAME%", "%DATE%", "%TIME%"], shell=True)
        .decode()
        .split()
    )
    check_dict = {}
    for check in checks:
        check_dict.setdefault(check.result.value, []).append(check)
    subs = {
        "model_path": model_path,
        "model_title": RasModel(model_path).prj_file.title,
        "checksuite": checksuite,
        "check_dict": check_dict,
        "tool_version": tool_version,
        "username": details[0],
        "day_name": details[1],
        "date": details[2],
        "time": details[3][:5],
        **theme.value,
    }
    with open(log_path, mode="w", encoding="utf-8") as log_file:
        log_file.write(BeautifulSoup(template.render(subs), "html.parser").prettify())
    return log_path


def res_dict_to_html_table(
    res_msg_dict: dict, html_color_str: str = "rgb(170, 170, 170)"
) -> str:
    html = f'<table border="0" style="line-height:1em; border-spacing:0; color:{html_color_str};">'
    for key, value in res_msg_dict.items():
        html += "<tr>"
        html += f"<th valign='top' align='left'>{key} :</th>"
        if isinstance(value, dict):
            html += (
                f"<td valign='top' align='left'>{res_dict_to_html_table(value)}</td>"
            )
        elif isinstance(value, list):
            html += f"<td valign='top' align='left'><table border='0'>"
            for item in value:
                html += "<tr>"
                if isinstance(item, dict):
                    html += f"<td valign='top' align='left'>{res_dict_to_html_table(item)}</td>"
                else:
                    html += f"<td valign='top' align='left'>{item}</td>"
                html += "</tr>"
            html += "</table></td>"
        else:
            html += f"<td valign='top' align='left'>{value}</td>"
        html += "</tr>"
    html += "</table>"
    return html
