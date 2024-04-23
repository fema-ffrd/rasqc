from rasqc.rasmodel import RasModel
from rasqc.result import RasqcResult

import os
from typing import List


class CheckSuite:
    checks: List 

    def __init__(self):
        self.checks = []

    def add_check(self, check):
        self.checks.append(check)

    def run_all(self, ras_model: str | os.PathLike | RasModel) -> List[RasqcResult]:
        results = []
        for check in self.checks:
            result = check.run(RasModel(ras_model))
            print(result)
            results.append(result)
        return results


check_suites = {
    "ffrd": CheckSuite(),
}


def register_check(suite_names: List[str]):
    def decorator(check_class):
        for suite_name in suite_names:
            if suite_name in check_suites:
                check_suites[suite_name].add_check(check_class())
            else:
                raise ValueError(f"Suite '{suite_name}' not found")
        return check_class
    return decorator
