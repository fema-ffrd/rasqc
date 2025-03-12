import rasqc.checkers
from rasqc.checksuite import CHECKSUITES
from rasqc.result import RasqcResultEncoder, ResultStatus, to_snake_case
from rasqc.log.writer import to_file, ColorTheme
from rasqc.rasmodel import RasModel

from rich.console import Console

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import sys
import webbrowser
from pathlib import Path
import pandas as pd
import geopandas as gpd


BANNER = r"""
  __|   _` |   __|   _` |   __| 
 |     (   | \__ \  (   |  (    
_|    \__._| ____/ \__. | \___| 
                       _|       
"""
with open(Path(__file__).parent.resolve() / "version.txt") as v:
    VERSION = v.read()


def run_console(ras_model: str, checksuite: str) -> None:
    console = Console()
    print(BANNER.strip("\n"), f"version {VERSION}")
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
    note_count = len(
        [result for result in results if result.result == ResultStatus.NOTE]
    )
    error_count = len(
        [result for result in results if result.result == ResultStatus.ERROR]
    )
    warning_count = len(
        [result for result in results if result.result == ResultStatus.WARNING]
    )
    ok_count = len([result for result in results if result.result == ResultStatus.OK])
    console.print("Results:", style="bold white")
    console.print(f"- Notes: [bold purple]{note_count}[/bold purple]")
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
    print(BANNER.strip("\n"), f"version {VERSION}")
    results = CHECKSUITES[checksuite].run_all_silent(ras_model)
    results_dicts = [asdict(result) for result in results]
    output = {
        "model": ras_model,
        "checksuite": checksuite,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": results_dicts,
    }
    print(json.dumps(output, cls=RasqcResultEncoder, indent=4))
    return output


def run_files(
    ras_model: str,
    checksuite: str,
    theme: ColorTheme = ColorTheme.NINETIES,
) -> None:
    print(BANNER.strip("\n"), f"version {VERSION}")
    results = CHECKSUITES[checksuite].run_all_silent(ras_model)
    gdfs = []
    for res in results:
        if res.gdf is not None:
            res.gdf_to_shp(ras_model=ras_model)
            res.gdf["check"] = res.name 
            gdfs.append(res.gdf)
    out_dir = Path(ras_model).parent / "rasqc"
    out_dir.mkdir(parents=True, exist_ok=True)
    gpd.GeoDataFrame(pd.concat(gdfs, axis=1)).to_file((out_dir / f"rasqc_{to_snake_case(RasModel(ras_model).prj_file.title)}").with_suffix(".shp")) if gdfs else None
    log_file = to_file(
        model_path=ras_model,
        checksuite=checksuite,
        checks=results,
        tool_version=VERSION,
        theme=theme,
    )
    webbrowser.open(log_file)


def main():
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
