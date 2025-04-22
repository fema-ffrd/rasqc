"""
rasqc - Automated HEC-RAS Model Quality Control Checks.

This package provides tools for checking HEC-RAS models against quality control
standards, particularly for FFRD (Federal Flood Risk Determination) models.
"""

# Import registry first to avoid circular imports
from .registry import *
from .checkers import *
from .check import *

from typing import List


def check_model(ras_model: str, checksuite: str) -> List[RasqcResult]:
    """Run a checksuite on a HEC-RAS model.

    Parameters
    ----------
        ras_model: Path to the HEC-RAS model to check.
        checksuite: The name of the checksuite to run.

    Returns
    -------
        None
    """
    results = CHECKSUITES[checksuite].run_checks(ras_model)
    return results
