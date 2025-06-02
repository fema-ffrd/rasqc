from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import subprocess
from bs4 import BeautifulSoup

from rasqc.result import RasqcResult, to_snake_case
from rasqc.rasmodel import RasModel
from .themes import ColorTheme


def to_file(
    model_path: str,
    checksuite: str,
    checks: list[RasqcResult],
    tool_version: str = "",
    theme: ColorTheme = ColorTheme.ARCADE,
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
            html += f"<td valign='top' align='left'>{res_dict_to_html_table(value, html_color_str)}</td>"
        elif isinstance(value, list):
            html += f"<td valign='top' align='left'><table border='0'>"
            for item in value:
                html += "<tr>"
                if isinstance(item, dict):
                    html += f"<td valign='top' align='left'>{res_dict_to_html_table(item, html_color_str)}</td>"
                else:
                    html += f"<td valign='top' align='left'>{item}</td>"
                html += "</tr>"
            html += "</table></td>"
        else:
            html += f"<td valign='top' align='left'>{value}</td>"
        html += "</tr>"
    html += "</table>"
    return html

def remove_json_seps(json_str: str, seps: list = ["{","}","[","]",","]) -> str:
    return json_str.translate(str.maketrans("", "", "".join(seps)))

def json_to_html_cleaned(
    json_str: str, html_color_str: str = "rgb(170, 170, 170)"
) -> str:
    return BeautifulSoup(f"<style>pre {{color: {html_color_str}}}</style>\n<pre>{remove_json_seps(json_str)}</pre>", features="html.parser").prettify()
