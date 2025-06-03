"""Main entry point for the rasqc command-line tool."""

from . import checkers  # noqa: F401
from .registry import CHECKSUITES
from .result import RasqcResultEncoder, ResultStatus
from .themes import ColorTheme
from .rasmodel import RasModel
from .utils import to_snake_case, results_to_html

from rich.console import Console

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import version
import json
import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd
import webbrowser

try:
    RASQC_VERSION = version("rasqc")
except:
    RASQC_VERSION = None


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
    console.print(
        f"[bold underline]rasqc: Automated HEC-RAS Model Quality Control Checks[/bold underline]"
    )
    console.print(
        f"[bold]Version[/bold]: [bright_blue]{RASQC_VERSION}[/bright_blue]",
        highlight=False,
    )
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
    results = CHECKSUITES[checksuite].run_checks_console(ras_model)
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
    results = CHECKSUITES[checksuite].run_checks(ras_model)
    results_dicts = [asdict(result) for result in results]
    output = {
        "version": RASQC_VERSION,
        "model": ras_model,
        "checksuite": checksuite,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": results_dicts,
    }
    print(json.dumps(output, cls=RasqcResultEncoder))
    return output


def run_files(
    ras_model: str,
    checksuite: str,
    theme: ColorTheme = ColorTheme.ARCADE,
    show_on_complete: bool = True,
) -> None:
    print(f"rasqc version {RASQC_VERSION}") if RASQC_VERSION else None
    results = CHECKSUITES[checksuite].run_checks(ras_model)
    out_dir = Path(ras_model).parent / "rasqc"
    out_dir.mkdir(parents=True, exist_ok=True)
    gdfs = []
    for res in results:
        if res.gdf is not None:
            shp_dir = out_dir / "shapes"
            shp_dir.mkdir(parents=True, exist_ok=True)
            res.gdf.to_file(
                (shp_dir / to_snake_case(res.name)).with_suffix(".shp"), SHPT="ARC"
            )
            res.gdf["check"] = res.name
            gdfs.append(res.gdf)
    out_shp = (
        out_dir / f"rasqc_{to_snake_case(RasModel(ras_model).prj_file.title)}"
    ).with_suffix(".shp")
    gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True)).to_file(
        out_shp,
        SHPT="ARC",
    ) if gdfs else None
    results_to_html(
        results=results,
        output_path=out_shp.with_suffix(".html"),
        model_path=ras_model,
        checksuite=checksuite,
        tool_version=RASQC_VERSION,
        theme=theme,
    )
    webbrowser.open(out_shp.with_suffix(".html")) if show_on_complete else None


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
    parser.add_argument(
        "--files",
        action="store_true",
        help="Output results to disk as HTML log and ESRI Shapefiles",
    )
    parser.add_argument(
        "--theme",
        type=str,
        default="NINETIES",
        choices=[t.name for t in ColorTheme],
        help="Color theme of output log file. Only used if the '--files' argument is specified. Default: 'NINETIES'",
    )
    args = parser.parse_args()
    if args.json:
        run_json(args.ras_model, args.checksuite)
    elif args.files:
        run_files(
            args.ras_model,
            args.checksuite,
            {ct.name: ct for ct in ColorTheme}[args.theme],
        )
    else:
        run_console(args.ras_model, args.checksuite)


if __name__ == "__main__":
    main()
