 # unittest-parallel

[![PyPI - Status](https://img.shields.io/pypi/status/unittest-parallel)](https://pypi.org/project/unittest-parallel/)
[![PyPI](https://img.shields.io/pypi/v/unittest-parallel)](https://pypi.org/project/unittest-parallel/)
[![GitHub](https://img.shields.io/github/license/craigahobbs/unittest-parallel)](https://github.com/craigahobbs/unittest-parallel/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unittest-parallel)](https://pypi.org/project/unittest-parallel/)

unittest-parallel is a parallel unit test runner for Python with coverage support.


## Run Unit Tests in Parallel

To run unittest-parallel, specify the directory containing your unit tests with the `-s` argument
and your package's top-level directory using the `-t` argument:

~~~
unittest-parallel -t . -s tests
~~~

By default, unittest-parallel runs tests using all CPU cores.

To run tests with coverage, add either the `--coverage` option (for line coverage) or the
`--coverage-branch` for line and branch coverage.

~~~
unittest-parallel -t . -s tests --coverage-branch
~~~


## Parallelism Level

By default, unittest-parallel runs test modules in parallel (`--level=module`). Here is the list of
all parallelism options:

- `--level=module` - Run test modules in parallel (default)

- `--level=class` - Run test classes in parallel. Use this option if you have
  [class fixtures](https://docs.python.org/3/library/unittest.html#class-and-module-fixtures).

- `--level=test` - Run individual tests in parallel. Using this option will likely fail if you have any
  [class or module fixtures](https://docs.python.org/3/library/unittest.html#class-and-module-fixtures).


## Speedup Potential

unittest-parallel provides the most significant speedups when you have *slow-running* unit tests and
many CPU cores. Slow-running tests are those that take considerably longer to run than an empty unit
test.

For projects with a large number of slow-running test modules (or classes or tests),
unittest-parallel with 2 CPU cores is roughly 2 times faster than `unittest discover`. With 4 CPU
cores, it is 4 times faster, and so on.

If you have few slow-running test modules (or classes or tests), running with unittest-parallel may
be slightly slower than `unittest discover`.

Theoretically, unittest-parallel with infinite CPU cores runs as long as your slowest test.


### Real-World Speedups

In a production application with thousands of slow-running unit tests, unittest-parallel with 4
CPU cores was 4 times faster than `unittest discover`.

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
