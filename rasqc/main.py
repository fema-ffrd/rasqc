"""Main entry point for the rasqc command-line tool."""

import rasqc.checkers # noqa: F401
from rasqc.checksuite import CHECKSUITES
from rasqc.result import RasqcResultEncoder, ResultStatus

from rich.console import Console

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import sys


BANNER = r"""
  __|   _` |   __|   _` |   __| 
 |     (   | \__ \  (   |  (    
_|    \__._| ____/ \__. | \___| 
                       _|       
"""


def run_console(ras_model: str, checksuite: str) -> None:
    """Run checks in console mode with rich formatting.

    Parameters
    ----------
        ras_model: Path to the HEC-RAS model .prj file.
        checksuite: Name of the checksuite to run.

    Returns
    -------
        None

    Exits
    -----
        With code 0 if all checks pass or there are only warnings.
        With code 1 if there are any errors.
    """
    console = Console()
    console.print(BANNER.strip("\n"))
    console.print(
        f"[bold]HEC-RAS Model[/bold]: [bright_blue]{ras_model}[/bright_blue]",
        highlight=False,
    )
    console.print(
        f"[bold]Checksuite[/bold]: [bright_blue]{checksuite}[/bright_blue]",
        highlight=False,
    )
    console.print(
        f"[bold]Timestamp[/bold]: [bright_blue]{datetime.now(timezone.utc).isoformat()}[/bright_blue]",
        highlight=False,
    )
    console.print(f"[bold]Checks[/bold]:")
    results = CHECKSUITES[checksuite].run_all(ras_model)
    error_count = len(
        [result for result in results if result.result == ResultStatus.ERROR]
    )
    warning_count = len(
        [result for result in results if result.result == ResultStatus.WARNING]
    )
    ok_count = len([result for result in results if result.result == ResultStatus.OK])
    console.print("Results:", style="bold white")
    console.print(f"- Errors: [bold red]{error_count}[/bold red]")
    console.print(f"- Warnings: [bold yellow]{warning_count}[/bold yellow]")
    console.print(f"- OK: [bold green]{ok_count}[/bold green]")
    if error_count > 0:
        console.print(f"❌ Finished with [bold red]errors[/bold red].")
        sys.exit(1)
    if warning_count > 0:
        console.print(f"⚠ Finished with [bold yellow]warnings[/bold yellow].")
        sys.exit(0)
    console.print(f"✔ All checks passed.")


def run_json(ras_model: str, checksuite: str) -> dict:
    """Run checks and output results as JSON.

    Parameters
    ----------
        ras_model: Path to the HEC-RAS model .prj file.
        checksuite: Name of the checksuite to run.

    Returns
    -------
        dict: Dictionary containing the check results.
    """
    results = CHECKSUITES[checksuite].run_all_silent(ras_model)
    results_dicts = [asdict(result) for result in results]
    output = {
        "model": ras_model,
        "checksuite": checksuite,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": results_dicts,
    }
    print(json.dumps(output, cls=RasqcResultEncoder))
    return output


def main():
    """Launch the rasqc command-line tool.

    Parses command-line arguments and runs the appropriate checks.
    """
    parser = argparse.ArgumentParser(
        description="rasqc: Automated HEC-RAS Model Quality Control Checks"
    )
    parser.add_argument("ras_model", type=str, help="HEC-RAS model .prj file")
    parser.add_argument(
        "--checksuite",
        type=str,
        default="ffrd",
        choices=CHECKSUITES.keys(),
        help="Checksuite to run. Default: ffrd",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()
    if args.json:
        run_json(args.ras_model, args.checksuite)
    else:
        run_console(args.ras_model, args.checksuite)


if __name__ == "__main__":
    main()
