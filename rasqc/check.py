"""Module for primary check function."""

from typing import List, Dict
from os import PathLike

from .checksuite import CheckSuite
from .rasmodel import RasModel
from .result import RasqcResult


# Dictionary of available check suites
CHECKSUITES: Dict[str, CheckSuite] = {"ffrd": CheckSuite(), "ble": CheckSuite()}


def register_check(suite_names: List[str]):
    """Register a checker with one or more check suites.

    Parameters
    ----------
        suite_names: List of suite names to register the checker with.

    Returns
    -------
        callable: Decorator function that registers the checker.

    Raises
    ------
        ValueError: If a suite name is not found in CHECKSUITES.
    """

    def decorator(check_class):
        """Register the decorated checker class with the specified suites.

        Parameters
        ----------
            check_class: The checker class to register.

        Returns
        -------
            The original checker class.

        Raises
        ------
            ValueError: If a suite name is not found in CHECKSUITES.
        """
        for suite_name in suite_names:
            if suite_name in CHECKSUITES:
                CHECKSUITES[suite_name].add_check(check_class())
            else:
                raise ValueError(f"Suite '{suite_name}' not found")
        return check_class

    return decorator


def check(
    ras_model: str | PathLike | RasModel, check_suite: str | CheckSuite
) -> List[RasqcResult]:
    """Run all checks on the provided HEC-RAS model.

    Parameters
    ----------
        ras_model: The HEC-RAS model to check.

    Returns
    -------
        List[RasqcResult]: List of results from all checks.
    """
    if isinstance(check_suite, str):
        check_suite: CheckSuite = CHECKSUITES[check_suite]
    return check_suite.run_checks(ras_model)
