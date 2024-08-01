import os
import sys
import subprocess
import unittest

import coverage
import coverage.exceptions as _cov_exceptions


TEST_DIR_NAME = "tests"
OMITTED_FILES = [
    "__init__.py",
    "tests/__main__.py",
    "server/fleetv2_http_api/models/*.py",
    "server/fleetv2_http_api/typing_utils.py",
    "server/fleetv2_http_api/util.py"
]
HTML_REPORT_FLAG = "-h"


def _report_coverage(cov: coverage.Coverage, html) -> None:
    if html:
        cov.html_report()
        subprocess.run(["open", "htmlcov/index.html"])
    else:
        try:
            cov.report()
        except _cov_exceptions.NoDataError:
            print("No data from coverage analysis to report.")
        except Exception as e:
            print(f"Problem reporting coverage. {e}")


def _run_tests(show_test_names: bool = True) -> None:
    possible_paths = [os.path.join(TEST_DIR_NAME, path) for path in sys.argv[1:]]
    if not possible_paths:
        paths = [TEST_DIR_NAME]
    else:
        paths = []
        for path in possible_paths:
            if os.path.exists(path):
                paths.append(path)
            else:
                print(f"Path '{path}' does not exist. Skipping.")
    suite = unittest.TestSuite()
    for path in paths:
        if os.path.isfile(path):
            file_name = os.path.basename(path)
            if file_name.endswith(".py"):
                pattern, dir = file_name, os.path.dirname(path)
        else:
            pattern, dir = "test_*.py", path
        suite.addTests(unittest.TestLoader().discover(dir, pattern=pattern))
    verbosity = 2 if show_test_names else 1
    unittest.TextTestRunner(verbosity=verbosity, buffer=True).run(suite)


if __name__ == "__main__":
    html = False
    if "-h" in sys.argv:
        html = True
        sys.argv.remove("-h")
    cov = coverage.Coverage(branch=True, omit=OMITTED_FILES)
    cov.start()
    _run_tests()
    cov.stop()
    cov.save()
    _report_coverage(cov, html)
