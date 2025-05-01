"""Utility functions."""

import json
from collections import defaultdict

import pandas as pd

from rasqc.result import RasqcResult, ResultStatus


def summarize_results(results: list[RasqcResult]) -> dict:
    """Create a json from a list of RasqcResults."""
    summary = {
        "passed": defaultdict(lambda: defaultdict(list)),
        "failed": defaultdict(lambda: defaultdict(list)),
    }

    for result in results:
        if result.result == ResultStatus.OK or result.result == ResultStatus.WARNING:
            group = "passed"
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
    """Create a json from a list of RasqcResults."""
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)


def results_to_excel(results: dict, output_path: str) -> None:
    """Create an excel from a json of RasqcResults. Creates 2 excel sheets for passed and failed."""

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
