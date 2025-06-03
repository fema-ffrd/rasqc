"""Module for registering and managing check suites."""

from .checksuite import CheckSuite, StacCheckSuite

from typing import Dict, List

# Dictionary of available check suites
CHECKSUITES: Dict[str, "CheckSuite"] = {
    "ffrd": CheckSuite(),
    "ras_stac_ffrd": StacCheckSuite(),
    "hms_stac_ffrd": StacCheckSuite(),
    "ble": CheckSuite(),
}


def register_check(suite_names: List[str], dependencies: List[str] = []):
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
                CHECKSUITES[suite_name].add_check(check_class(), dependencies)
            else:
                raise ValueError(f"Suite '{suite_name}' not found.")
        return check_class

    return decorator
