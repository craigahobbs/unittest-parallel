unittest_parallel
=================

unittest_parallel is a parallel unittest runner for Python with coverage support.

NOTE: The [coverage](https://pypi.org/project/coverage/) module must be installed for coverage support.

```
usage: unittest-parallel [-h] [-v] [-q] [-j COUNT] [--version] [-s START]
                         [-p PATTERN] [-t TOP] [--coverage]
                         [--coverage-branch] [--coverage-rcfile RCFILE]
                         [--coverage-include PAT] [--coverage-omit PAT]
                         [--coverage-source SRC] [--coverage-html DIR]
                         [--coverage-xml FILE] [--coverage-fail-under MIN]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -q, --quiet           Quiet output
  -j COUNT, --jobs COUNT
                        The number of test processes (default is 0, all cores)
  --version             show version number and quit

Unittest options:
  -s START, --start-directory START
                        Directory to start discovery ('.' default)
  -p PATTERN, --pattern PATTERN
                        Pattern to match tests ('test*.py' default)
  -t TOP, --top-level-directory TOP
                        Top level directory of project (defaults to start
                        directory)

Coverage options:
  --coverage            Run tests with coverage.
  --coverage-branch     Run tests with branch coverage.
  --coverage-rcfile RCFILE
                        Specify coverage configuration file.
  --coverage-include PAT
                        Include only files matching one of these patterns.
                        Accepts shell-style (quoted) wildcards.
  --coverage-omit PAT   Omit files matching one of these patterns. Accepts
                        shell-style (quoted) wildcards.
  --coverage-source SRC
                        A list of packages or directories of code to be
                        measured.
  --coverage-html DIR   Generate coverage HTML report.
  --coverage-xml FILE   Generate coverage XML report.
  --coverage-fail-under MIN
                        Fail if coverage percentage under min.
```
