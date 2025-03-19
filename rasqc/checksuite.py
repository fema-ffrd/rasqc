"""Module for defining and managing check suites for HEC-RAS model quality control."""

from .base_checker import RasqcChecker
from .rasmodel import RasModel
from .result import RasqcResult, ResultStatus

from rich.console import Console

import os
import re
from typing import List


def _bold_single_quotes(text: str) -> str:
    """Format text by making content within single quotes bold and cyan.

    Parameters
    ----------
        text: The text to format.

    Returns
    -------
        str: The formatted text with rich markup for bold cyan text within single quotes.
    """
    # Regex to find text within single quotes
    pattern = re.compile(r"'(.*?)'")

    # Replace matches with bold tags
    formatted_text = pattern.sub(r"[bold cyan]'\1'[/bold cyan]", text)

    return formatted_text


class CheckSuite:
    """A suite of quality control checks to run on a HEC-RAS model.

    Attributes
    ----------
        checks: List of RasqcChecker instances to run.
    """

    checks: List[RasqcChecker]

    def __init__(self):
        """Initialize an empty check suite."""
        self.checks = []

    def add_check(self, check):
        """Add a checker to the suite.

        Parameters
        ----------
            check: The RasqcChecker instance to add.
        """
        self.checks.append(check)

    def run_checks_console(
        self, ras_model: str | os.PathLike | RasModel
    ) -> List[RasqcResult]:
        """Run all checks in the suite and print results to the console.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check, either as a path or RasModel instance.

        Returns
        -------
            List[RasqcResult]: The results of all checks.
        """
        results = []
        console = Console()
        for check in self.checks:
            result = check.run(RasModel(ras_model))
            if result.message:
                message = _bold_single_quotes(result.message)
            console.print(f"- {check.name}: ", end="")
            if result.result == ResultStatus.ERROR:
                console.print("ERROR", style="bold red")
                console.print(f"    {message}", highlight=False, style="gray50")
            elif result.result == ResultStatus.WARNING:
                console.print("WARNING", style="bold yellow")
                console.print(f"    {message}", style="gray50")
            else:
                console.print("OK", style="bold green")
            results.append(result)
        return results

    def run_checks(self, ras_model: str | os.PathLike | RasModel) -> List[RasqcResult]:
        """Run all checks in the suite.

        Parameters
        ----------
            ras_model: The HEC-RAS model to check, either as a path or RasModel instance.

        Returns
        -------
            List[RasqcResult]: The results of all checks.
        """
        results = []
        for check in self.checks:
            results.append(check.run(RasModel(ras_model)))
        return results
