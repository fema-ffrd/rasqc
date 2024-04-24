from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult, ResultStatus

from rich.console import Console

import os
from typing import List
from time import sleep


class CheckSuite:
    checks: List 

    def __init__(self):
        self.checks = []

    def add_check(self, check):
        self.checks.append(check)

    def run_all(self, ras_model: str | os.PathLike | RasModel) -> List[RasqcResult]:
        results = []
        console = Console()
        for check in self.checks:
            result = check.run(RasModel(ras_model))
            console.print(f"- {check.name}: ", end="")
            if result.result == ResultStatus.ERROR:
                console.print("ERROR", style="bold red")
                console.print(f"\t{result.message}", highlight=False, style="gray50")
            elif result.result == ResultStatus.WARNING:
                console.print("WARNING", style="bold yellow")
                console.print(f"\t{result.message}", style="gray50")
            else:
                console.print("OK", style="bold green")
            results.append(result)
        return results

    def run_all_silent(self, ras_model: str | os.PathLike | RasModel) -> List[RasqcResult]:
        results = []
        for check in self.checks:
            results.append(check.run(RasModel(ras_model)))
        return results


CHECKSUITES = {
    "ffrd": CheckSuite(),
}


def register_check(suite_names: List[str]):
    def decorator(check_class):
        for suite_name in suite_names:
            if suite_name in CHECKSUITES:
                CHECKSUITES[suite_name].add_check(check_class())
            else:
                raise ValueError(f"Suite '{suite_name}' not found")
        return check_class
    return decorator
