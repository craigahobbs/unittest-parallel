# unittest-parallel

![PyPI - Status](https://img.shields.io/pypi/status/unittest-parallel)
![PyPI](https://img.shields.io/pypi/v/unittest-parallel)
![GitHub](https://img.shields.io/github/license/craigahobbs/unittest-parallel)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unittest-parallel)

unittest-parallel is a parallel unit test runner for Python with coverage support.

To run unittest-parallel, specify the directory containing your unit tests with the "-s" argument
and your package's top-level directory using the "-t" argument:

```
unittest-parallel -t . -s tests
```

By default, unittest-parallel runs unit tests on all CPU cores available.

To run your unit tests with coverage, add either the "--coverage" option (for line coverage) or the
"--coverage-branch" for line and branch coverage.

```
unittest-parallel -t . -s tests --coverage-branch
```


## Links

- [Package on pypi](https://pypi.org/project/unittest-parallel/)
- [Source code on GitHub](https://github.com/craigahobbs/unittest-parallel)


## How it works

unittest-parallel uses Python's built-in unit test discovery to find all test cases in your project.
It then runs all test cases in a Python multi-processing pool of the requested size.

### Class and Module Fixtures

Python's unittest framework supports
[class and module fixtures.](https://docs.python.org/3/library/unittest.html#class-and-module-fixtures)
Use the "--class-fixtures" option to execute class fixtures correctly. Use the "--module-fixtures"
option to execute module fixtures correctly. Note that these options reduce the amount of
parallelism.


## Example output

```
$ unittest-parallel -v -t src -s src/tests --coverage-branch --coverage-fail-under 100

test_array (tests.test_encode.TestDecodeQueryString) ... ok
test_array_initial_non_zero (tests.test_encode.TestDecodeQueryString) ... ok
test_negative_index (tests.test_encode.TestDecodeQueryString) ... ok
...
test_struct_empty (tests.test_schema.TestValidateTypeModelTypes) ... ok
test_struct_base (tests.test_schema.TestValidateTypeModelTypes) ... ok
test_struct_inconsistent_type_name (tests.test_schema.TestValidateTypeModelTypes) ... ok

----------------------------------------------------------------------
Ran 298 tests in 0.708s

OK

Name                                 Stmts   Miss Branch BrPart  Cover
----------------------------------------------------------------------
src/schema_markdown/__init__.py          5      0      0      0   100%
src/schema_markdown/__main__.py          3      0      0      0   100%
src/schema_markdown/encode.py           84      0     60      0   100%
...
src/tests/test_main.py                 179      0      4      0   100%
src/tests/test_parser.py               363      0      0      0   100%
src/tests/test_schema.py               828      0      0      0   100%
----------------------------------------------------------------------
TOTAL                                 2412      0    571      0   100%

Total coverage is 100.00%
```


## Usage

```
usage: unittest-parallel [-h] [-v] [-q] [-b] [-j COUNT] [--version] [-s START]
                         [-p PATTERN] [-t TOP] [--coverage]
                         [--coverage-branch] [--coverage-rcfile RCFILE]
                         [--coverage-include PAT] [--coverage-omit PAT]
                         [--coverage-source SRC] [--coverage-html DIR]
                         [--coverage-xml FILE] [--coverage-fail-under MIN]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -q, --quiet           Quiet output
  -b, --buffer          Buffer stdout and stderr during tests
  -j COUNT, --jobs COUNT
                        The number of test processes (default is 0, all cores)
  --version             show version number and quit

unittest options:
  -s START, --start-directory START
                        Directory to start discovery ('.' default)
  -p PATTERN, --pattern PATTERN
                        Pattern to match tests ('test*.py' default)
  -t TOP, --top-level-directory TOP
                        Top level directory of project (defaults to start
                        directory)

coverage options:
  --coverage            Run tests with coverage
  --coverage-branch     Run tests with branch coverage
  --coverage-rcfile RCFILE
                        Specify coverage configuration file
  --coverage-include PAT
                        Include only files matching one of these patterns.
                        Accepts shell-style (quoted) wildcards.
  --coverage-omit PAT   Omit files matching one of these patterns. Accepts
                        shell-style (quoted) wildcards.
  --coverage-source SRC
                        A list of packages or directories of code to be
                        measured
  --coverage-html DIR   Generate coverage HTML report
  --coverage-xml FILE   Generate coverage XML report
  --coverage-fail-under MIN
                        Fail if coverage percentage under min
```


## Development

This project is developed using [Python Build](https://github.com/craigahobbs/python-build#readme).
