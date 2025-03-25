"""Module for defining and managing check suites for HEC-RAS model quality control."""

from .base_checker import RasqcChecker
from .rasmodel import RasModel
from .result import RasqcResult, ResultStatus

import networkx as nx
from rich.console import Console
from rich.markup import escape

from collections import defaultdict
import os
import re
from typing import Dict, List


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

    checks: Dict[str, RasqcChecker]
    dependencies: Dict[str, set]

    def __init__(self):
        """Initialize an empty check suite."""
        self.checks = {}
        self.dependencies = {}

    def add_check(self, check: RasqcChecker, dependencies: List[str] = []):
        """Add a checker to the suite.

        Parameters
        ----------
            check: The RasqcChecker instance to add.
        """
        check_name = check.__class__.__name__
        self.checks[check_name] = check
        if check_name not in self.dependencies:
            self.dependencies[check_name] = set()
        self.dependencies[check_name].update(dependencies)

    def get_execution_order(self) -> List[str]:
        """Return checks in dependency order using topological sorting."""
        graph = nx.DiGraph()
        for check, deps in self.dependencies.items():
            graph.add_node(check)
            for dep in deps:
                graph.add_edge(dep, check)
        return list(nx.topological_sort(graph))

    @staticmethod
    def _print_result(console: Console, check: RasqcChecker, result: RasqcResult):
        """Print the result of a check to the console.

        Parameters
        ----------
            result: The RasqcResult to print.
        """
        if result.message:
            message = _bold_single_quotes(result.message)
        console.print(f"[{result.filename}] - {check.name}: ", end="")
        if result.result == ResultStatus.ERROR:
            console.print("ERROR", style="bold red")
            console.print(f"    {message}", highlight=False, style="gray50")
        elif result.result == ResultStatus.WARNING:
            console.print("WARNING", style="bold yellow")
            console.print(f"    {message}", style="gray50")
        else:
            console.print("OK", style="bold green")
        if not result.result == ResultStatus.OK and result.pattern:
            console.print(
                f"    Required pattern: {escape(result.pattern)}",
                highlight=False,
                style="gray50",
            )

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
        ordered_checks = self.get_execution_order()
        ras_model = RasModel(ras_model)
        for check_name in ordered_checks:
            check = self.checks[check_name]
            result = check.run(ras_model)
            if type(result) is RasqcResult:
                self._print_result(console, check, result)
                results.append(result)
            elif type(result) is list:
                for r in result:
                    self._print_result(console, check, r)
                    results.append(r)
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
        ordered_checks = self.get_execution_order()
        ras_model = RasModel(ras_model)
        for check_name in ordered_checks:
            check = self.checks[check_name]
            result = check.run(ras_model)
            if type(result) is list:
                results.extend(result)
            else:
                results.append(result)
        return results
