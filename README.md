# unittest-parallel

[![PyPI - Status](https://img.shields.io/pypi/status/unittest-parallel)](https://pypi.org/project/unittest-parallel/)
[![PyPI](https://img.shields.io/pypi/v/unittest-parallel)](https://pypi.org/project/unittest-parallel/)
[![GitHub](https://img.shields.io/github/license/craigahobbs/unittest-parallel)](https://github.com/craigahobbs/unittest-parallel/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unittest-parallel)](https://pypi.org/project/unittest-parallel/)

unittest-parallel is a parallel unit test runner for Python with coverage support.


## Run Tests in Parallel

Install unittest-parallel from PyPI:

~~~
pip install unittest-parallel
~~~

unittest-parallel discovers tests like `python -m unittest discover`. Specify the directory
containing your tests with `-s` and the project's top-level directory with `-t`:

~~~
unittest-parallel -t . -s tests
~~~

By default, unittest-parallel runs tests using all CPU cores.


### Test Coverage

To run tests with coverage, add `--coverage` (line coverage) or `--coverage-branch` (line and
branch coverage):

~~~
unittest-parallel -t . -s tests --coverage-branch
~~~

Add `--coverage-html DIR` or `--coverage-xml FILE` to write a report, and
`--coverage-fail-under MIN` to fail the run if coverage is below `MIN`. Coverage from all
workers is combined, including import-time code executed during discovery.


### Parallelism Level

By default, unittest-parallel runs test modules in parallel (`--level=module`), which works with
[class and module fixtures](https://docs.python.org/3/library/unittest.html#class-and-module-fixtures).
The parallelism options are:

- `--level=module` - Run test modules in parallel (default). Module fixtures run once per module.

- `--level=class` - Run test classes in parallel. Class fixtures run once per class. Module
  fixtures (`setUpModule`) run once per class and may run concurrently, so use `--level=module`
  if you have module fixtures.

- `--level=test` - Run individual tests in parallel. This will likely fail if you have any
  [class or module fixtures](https://docs.python.org/3/library/unittest.html#class-and-module-fixtures).


### Process and Thread Pools

By default, unittest-parallel uses a process pool. Worker processes are reused across test suites.
Use `--disable-process-pooling` to run each suite in a fresh process if suites leak process-global
state.

`--thread` uses a thread pool instead of a process pool. It works on CPython with the GIL and on
[free-threaded Python](https://docs.python.org/3/howto/free-threading-python.html), but it only
improves performance on free-threaded Python, where threads can run CPU-bound tests on multiple
cores without process-startup overhead.

Do not use `--thread` with `unittest.mock`, since mocks patch global state shared by all threads.
`-b` / `--buffer` is ignored with `--thread`.


### Custom Runner and Result

`--runner` and `--result` take a class as `<module>.<class>`.

When `--result` is set, the result class reports errors itself; unittest-parallel does not reprint
them. When `--runner` or `--result` is set, the combined `Ran N tests` summary is omitted (workers
may still print their own).


## Speedup Potential

When you have many independent test modules that take longer to run than the cost of
parallelization, unittest-parallel typically speeds up `unittest discover` by about the number of
CPU cores. With 4 cores that is about 4 times faster; with 8 cores, about 8 times faster.

If most tests are very short, you may see little speedup, or a slowdown, compared to
`unittest discover`.


### I/O-Bound Tests

If your tests are I/O-bound (for example, they call web services), you may benefit from using more
workers than CPU cores (`-j`):

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
                         [--disable-process-pooling] [--thread] [--coverage]
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
  -j, --jobs COUNT      The number of test workers (default is 0, all cores)
  --level {module,class,test}
                        Set the test parallelism level (default is 'module')
  --disable-process-pooling
                        Do not reuse processes used to run test suites
  --thread              Use a thread pool for parallelization

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
