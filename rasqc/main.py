import rasqc.checkers
from rasqc.checksuite import check_suites
from rasqc.result import RasqcResultEncoder, ResultStatus

from rich.console import Console

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import sys


BANNER = """
  __|   _` |   __|   _` |   __| 
 |     (   | \__ \  (   |  (    
_|    \__._| ____/ \__. | \___| 
                       _|       
"""


def run_console(ras_model: str) -> None:
    console = Console()
    console.print(BANNER.strip("\n"))
    console.print(f"[bold]HEC-RAS Model[/bold]: [bright_blue]{ras_model}[/bright_blue]", highlight=False)
    console.print(f"[bold]Checksuite[/bold]: [bright_blue]FFRD[/bright_blue]", highlight=False)
    console.print(f"[bold]Timestamp[/bold]: [bright_blue]{datetime.now(timezone.utc).isoformat()}[/bright_blue]", highlight=False)
    console.print(f"[bold]Checks[/bold]:")
    results = check_suites["ffrd"].run_all(ras_model)
    error_count = len([result for result in results if result.result == ResultStatus.ERROR])
    warning_count = len([result for result in results if result.result == ResultStatus.WARNING])
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


def run_json(ras_model: str) -> None:
    results = check_suites["ffrd"].run_all_json(ras_model)
    results_dicts = [asdict(result) for result in results]
    output = {
        "model": ras_model,
        "checksuite": "ffrd",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": results_dicts
    }
    print(json.dumps(output, cls=RasqcResultEncoder))


def main():
    parser = argparse.ArgumentParser(description='rasqc: Automated HEC-RAS Model Quality Control Checks')
    parser.add_argument('ras_model', type=str, help='HEC-RAS model .prj file')
    parser.add_argument('--checksuite', type=str, default='ffrd', choices=check_suites.keys(),
                        help='Checksuite to run. Default: ffrd')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    args = parser.parse_args()
    if args.json:
        run_json(args.ras_model)
    else:
        run_console(args.ras_model)


if __name__ == "__main__":
    main()
