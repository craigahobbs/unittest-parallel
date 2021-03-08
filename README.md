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

The [coverage](https://pypi.org/project/coverage/) module is required for coverage support.


## How it works

unittest-parallel uses Python's built-in unit test discovery to find all the test suites (TestCase
classes) in your project. It then runs each test suite in a Python multi-processing pool of the
requested size. Thus, the more test suites your unit tests are broken into, the better
parallelization you'll get in your unit test runs.


## Links

- [Package on pypi](https://pypi.org/project/unittest-parallel/)
- [Source code on GitHub](https://github.com/craigahobbs/unittest-parallel)


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
Refer to the Python Build [documentation](https://github.com/craigahobbs/python-build#make-targets)
for development instructions.
