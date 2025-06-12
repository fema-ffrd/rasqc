"""Utility functions."""

import json
from collections import defaultdict
import re
from bs4 import BeautifulSoup
from pathlib import Path
import subprocess
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from typing import Literal, List

from .result import RasqcResult, ResultStatus
from .rasmodel import RasModel
from .themes import ColorTheme


def summarize_results(results: list[RasqcResult]) -> dict:
    """Create a dict from a list of RasqcResults."""
    summary = {
        "passed": defaultdict(lambda: defaultdict(list)),
        "failed": defaultdict(lambda: defaultdict(list)),
    }

    for result in results:
        if result.result == ResultStatus.OK or result.result == ResultStatus.WARNING:
            group = "passed"
        elif result.result == ResultStatus.NOTE:
            group = "note"
        else:
            group = "failed"
        check_name = result.name
        filename = result.filename

        if result.element and isinstance(result.element, str):
            value = result.element
        else:
            value = "N/A"

        summary[group][check_name][filename].append(value)

    return {
        "passed": {k: dict(v) for k, v in summary["passed"].items()},
        "failed": {k: dict(v) for k, v in summary["failed"].items()},
    }


def results_to_json(results: dict, output_path: str) -> None:
    """Create a json from a dict of RasqcResults."""
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)


def results_to_excel(results: dict, output_path: str) -> None:
    """Create an excel from a dict of RasqcResults. Creates 2 excel sheets for passed and failed."""

    def flatten(group_name):
        rows = []
        for pattern, files in results.get(group_name, {}).items():
            for file, props in files.items():
                for prop in props:
                    rows.append(
                        {
                            "Pattern Name": pattern,
                            "File Name": file,
                            "RAS Property Name": prop,
                        }
                    )
        return pd.DataFrame(rows)

    passed_df = flatten("passed")
    failed_df = flatten("failed")

    with pd.ExcelWriter(output_path) as writer:
        failed_df.to_excel(writer, sheet_name="failed", index=False)
        passed_df.to_excel(writer, sheet_name="passed", index=False)


def to_snake_case(text: str) -> str:
    """Convert a string to snake case."""
    text = re.sub(r"[-]", " ", text)
    text = "".join([" " + c.lower() if c.isupper() else c for c in text]).lstrip()
    return re.sub(r"\s+", "_", text)


def remove_json_seps(json_str: str, seps: list = ["{", "}", "[", "]", ","]) -> str:
    """Remove a list of seporator characters from a JSON string."""
    return json_str.translate(str.maketrans("", "", "".join(seps)))


def dict_to_html_string(
    dictionary: dict, color_code: str = "rgb(170, 170, 170)"
) -> str:
    """Convert a python dictionary to an HTML string with a clean look."""
    return BeautifulSoup(
        f"<style>pre {{color: {color_code}}}</style>\n<pre>{remove_json_seps(json.dumps(dictionary, indent=4))}</pre>",
        features="html.parser",
    ).prettify()


def dict_to_html_table(dictionary: dict, color_code: str = "rgb(170, 170, 170)") -> str:
    """Convert a python dictionary to an HTML table string."""
    html = f'<table border="0" style="line-height:1em; border-spacing:0; color:{color_code};">'
    for key, value in dictionary.items():
        html += "<tr>"
        html += f"<th valign='top' align='left'>{key} :</th>"
        if isinstance(value, dict):
            html += f"<td valign='top' align='left'>{dict_to_html_table(value, color_code)}</td>"
        elif isinstance(value, list):
            html += f"<td valign='top' align='left'><table border='0'>"
            for item in value:
                html += "<tr>"
                if isinstance(item, dict):
                    html += f"<td valign='top' align='left'>{dict_to_html_table(item, color_code)}</td>"
                else:
                    html += f"<td valign='top' align='left'>{item}</td>"
                html += "</tr>"
            html += "</table></td>"
        else:
            html += f"<td valign='top' align='left'>{value}</td>"
        html += "</tr>"
    html += "</table>"
    return BeautifulSoup(html, features="html.parser").prettify()


def is_valid_json(json_str: str) -> bool:
    """Check if string is a valid JSON string."""
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False


def group_results(results: List[RasqcResult]) -> dict:
    """
    Groups a list of RasqcResult objects into a dict based on
    whether the result is from a 'note' or 'check', then based
    on the name of the RasqcResult object.

    Parameters
    ----------
        results: A list of RasqcResult objects.

    Returns
    -------
        dict: A dict of RasqcResult objects in pattern {'note' or 'check': {result name: [results]}}.
    """  # noqa D401
    results_dict = {}
    for result in results:
        results_dict.setdefault(
            "note" if result.result.value == "note" else "check", {}
        ).setdefault(result.name, []).append(result)
    return results_dict


def results_to_html(
    results: list[RasqcResult],
    output_path: str,
    model_path: str,
    checksuite: str,
    message_style: Literal["table", "indent"] = "table",
    tool_version: str = None,
    theme: ColorTheme = ColorTheme.ARCADE,
) -> None:
    """Create an HTML file from a list of RasqcResults."""
    env = Environment(loader=FileSystemLoader(Path(__file__).parent.resolve()))
    env.globals.update(
        dict_to_html_table=dict_to_html_table,
        dict_to_html_string=dict_to_html_string,
        message_style=message_style,
        is_valid_json=is_valid_json,
        loads=json.loads,
    )
    template = env.get_template("template.html")
    details = (
        subprocess.check_output(["echo", "%USERNAME%", "%DATE%", "%TIME%"], shell=True)
        .decode()
        .split()
    )
    results_dict = group_results(results)
    subs = {
        "model_path": model_path,
        "model_title": RasModel(model_path).prj_file.title,
        "checksuite": checksuite,
        "results_dict": results_dict,
        "tool_version": tool_version,
        "username": details[0],
        "day_name": details[1],
        "date": details[2],
        "time": details[3][:5],
        **theme.value,
    }
    with open(output_path, mode="w", encoding="utf-8") as log_file:
        log_file.write(BeautifulSoup(template.render(subs), "html.parser").prettify())
