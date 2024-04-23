import rasqc.checkers
from rasqc.checksuite import check_suites
from rasqc.result import ResultStatus

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='rasqc: Automated HEC-RAS Model Quality Control')
    parser.add_argument('ras_model', type=str, help='HEC-RAS model .prj file')
    args = parser.parse_args()
    results = check_suites["ffrd"].run_all(args.ras_model)
    if not all(result.result == ResultStatus.OK for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
