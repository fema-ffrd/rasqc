# rasqc

Automated QA/QC checks on [HEC-RAS](https://www.hec.usace.army.mil/software/hec-ras/) models.

*Pronunciation: `raz·kju·si`*

## Developer Setup

Create a virtual environment in the project directory:
```shell
$ python -m venv venv-rasqc
```

Activate the virtual environment:
```shell
# For macOS/Linux
$ source ./venv-rasqc/bin/activate
```
```shell
# For Windows
$ ./venv-rashdf/Scripts/activate
```

Install dev dependencies:
```shell
(venv-rasqc) $ pip install ".[dev]"
```

## Code Formatting

```shell
(venv-rasqc) $ ruff format
```

## Unit Testing

```shell
(venv-rasqc) $ pytest
```

## Run

```shell
(venv-rasqc) $ python -m rasqc.cli --help
```

## Build Console App

```shell
(venv-rasqc) $ pyinstaller "./rasqc/cli.py" --name rasqc --onefile --collect-all pyogrio --add-data "./rasqc/template.html:./rasqc"
```

## CLI

The `rasqc` command-line interface allows export directly to a variety of formats.
```shell
$ & "rasqc.exe" ras_model [--checksuite] [--theme] [<options$]
```

CLI help:
```shell
$ & "rasqc.exe" --help
```

Example: run the "ble" checksuite and write output files to the disk ({model root folder}/rasqc):
```shell
$ & "rasqc.exe" "Muncie.prj" --checksuite ble --files
```

Example: run the "ble" checksuite and write results to `stdout`:
```shell
$ & "rasqc.exe" "Muncie.prj" --checksuite ble
```

Example: run the "ble" checksuite, print results as `GeoJSON`, and return a `dict` of results:
```shell
$ & "rasqc.exe" "Muncie.prj" --checksuite ble --json
```
