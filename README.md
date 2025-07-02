 # unittest-parallel

[![PyPI - Status](https://img.shields.io/pypi/status/unittest-parallel)](https://pypi.org/project/unittest-parallel/)
[![PyPI](https://img.shields.io/pypi/v/unittest-parallel)](https://pypi.org/project/unittest-parallel/)
[![GitHub](https://img.shields.io/github/license/craigahobbs/unittest-parallel)](https://github.com/craigahobbs/unittest-parallel/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unittest-parallel)](https://pypi.org/project/unittest-parallel/)

unittest-parallel is a parallel unit test runner for Python with coverage support.


## Run Tests in Parallel

To run tests in parallel with unittest-parallel, specify the directory containing your unit tests
with the `-s` argument and your package's top-level directory using the `-t` argument:

~~~
unittest-parallel -t . -s tests
~~~

By default, unittest-parallel runs tests using all CPU cores.


### Test Coverage

To run tests with coverage, add either the `--coverage` option (for line coverage) or the
`--coverage-branch` for line and branch coverage.

~~~
unittest-parallel -t . -s tests --coverage-branch
~~~


### Parallelism Level

By default, unittest-parallel runs test modules in parallel (`--level=module`). Here is the list of
all parallelism options:

- `--level=module` - Run test modules in parallel (default)

- `--level=class` - Run test classes in parallel. Use this option if you have
  [class fixtures](https://docs.python.org/3/library/unittest.html#class-and-module-fixtures).

- `--level=test` - Run individual tests in parallel. Using this option will likely fail if you have any
  [class or module fixtures](https://docs.python.org/3/library/unittest.html#class-and-module-fixtures).


## Speedup Potential

Generally speaking, unittest-parallel will run your unit tests faster by a factor of the number of
CPU cores you have, as compared to `unittest discover`.

In other words, if you have 4 CPU cores, unittest-parallel will run your tests 4 times faster. If
you have 8 CPU cores, it will run 8 times faster, and so on.

Note that you may see less benefit from unittest-parallel if your average test duration is short
compared to the underlying cost of parallelization.


### I/O-Bound Tests

If your tests are I/O-bound (e.g., call web services), you may benefit from using a higher number of
test processes (`-j`). In the following case, the I/O-bound tests run 100 times faster.

~~~
unittest-parallel -j 100 -t . -s tests
~~~


### Real-World Speedups

I wrote unittest-parallel for a large production backend API application with thousands of unit
tests. As expected, unittest-parallel ran tests 4 times faster using 4 cores, compared to `unittest
discover`.

[A user reports](https://github.com/craigahobbs/unittest-parallel/issues/24) that their tests
ran 20 times faster on their development machine and 6 times faster on their test machine.

[Another user](https://github.com/craigahobbs/unittest-parallel/issues/5) reports that "it shaved
70% off the runtime of my painfully long integration tests."

[Another user](https://github.com/craigahobbs/unittest-parallel/issues/3) reports that "tests take
2x less times to run."


## Usage

~~~
usage: unittest-parallel [-h] [-v] [-q] [-f] [-b] [-k TESTNAMEPATTERNS]
                         [-s START] [-p PATTERN] [-t TOP] [--runner RUNNER]
                         [--result RESULT] [-j COUNT]
                         [--level {module,class,test}]
                         [--disable-process-pooling] [--coverage]
                         [--coverage-branch] [--coverage-rcfile RCFILE]
                         [--coverage-include PAT] [--coverage-omit PAT]
                         [--coverage-source SRC] [--coverage-html DIR]
                         [--coverage-xml FILE] [--coverage-fail-under MIN]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -q, --quiet           Quiet output
  -f, --failfast        Stop on first fail or error
  -b, --buffer          Buffer stdout and stderr during tests
  -k TESTNAMEPATTERNS   Only run tests which match the given substring
  -s, --start-directory START
                        Directory to start discovery ('.' default)
  -p, --pattern PATTERN
                        Pattern to match tests ('test*.py' default)
  -t, --top-level-directory TOP
                        Top level directory of project (defaults to start
                        directory)
  --runner RUNNER       Custom unittest runner class <module>.<class>
  --result RESULT       Custom unittest result class <module>.<class>

parallelization options:
  -j, --jobs COUNT      The number of test processes (default is 0, all cores)
  --level {module,class,test}
                        Set the test parallelism level (default is 'module')
  --disable-process-pooling
                        Do not reuse processes used to run test suites

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
~~~


## Development

This package is developed using [python-build](https://github.com/craigahobbs/python-build#readme).
It was started using [python-template](https://github.com/craigahobbs/python-template#readme) as follows:

~~~
template-specialize python-template/template/ unittest-parallel/ -k package unittest-parallel -k name 'Craig A. Hobbs' -k email 'craigahobbs@gmail.com' -k github 'craigahobbs' -k noapi 1
~~~
