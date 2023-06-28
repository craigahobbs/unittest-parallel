# unittest-parallel

[![PyPI - Status](https://img.shields.io/pypi/status/unittest-parallel)](https://pypi.org/project/unittest-parallel/)
[![PyPI](https://img.shields.io/pypi/v/unittest-parallel)](https://pypi.org/project/unittest-parallel/)
[![GitHub](https://img.shields.io/github/license/craigahobbs/unittest-parallel)](https://github.com/craigahobbs/unittest-parallel/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unittest-parallel)](https://pypi.org/project/unittest-parallel/)

unittest-parallel is a parallel unit test runner for Python with coverage support.


## Links

- [Source code](https://github.com/craigahobbs/unittest-parallel)


## Run Unit Tests in Parallel

To run unittest-parallel, specify the directory containing your unit tests with the `-s` argument
and your package's top-level directory using the `-t` argument:

~~~
unittest-parallel -t . -s tests
~~~

By default, unittest-parallel runs unit test modules on all CPU cores available.

To run your unit tests with coverage, add either the `--coverage` option (for line coverage) or the
`--coverage-branch` for line and branch coverage.

~~~
unittest-parallel -t . -s tests --coverage-branch
~~~


## Parallelism Level

By default, unittest-parallel runs test modules in parallel, which works with
[test class and module fixtures](https://docs.python.org/3/library/unittest.html#class-and-module-fixtures).
If you don't have any module fixtures, you can use the `--level=class` option to run test classes in
parallel. If you don't have any module or class fixtures, you can use the `--level=test` option to
run individual tests in parallel.


## Do I Need unittest-parallel?

unittest-parallel helps the most when you have many long-running unit tests, such as those that make
web service calls or are compute-intensive. If you just have many fast-running unit tests,
unittest-parallel may slow down unit test execution due to the cost of parallelization.

For example, for one of my projects with thousands of compute-intensive unit tests, running tests
with unittest-parallel is **five times faster** than running tests using Python's built-in unit test
runner.

For another project, with hundreds of fast-running unit tests, running tests using unittest-parallel
is **twice as slow** as running them using Python's built-in unit test runner.

To determine if unittest-parallel will improve your unit test run times, you'll need to try it on
your project.


## Development

This package is developed using [python-build](https://github.com/craigahobbs/python-build#readme).
It was started using [python-template](https://github.com/craigahobbs/python-template#readme) as follows:

~~~
template-specialize python-template/template/ unittest-parallel/ -k package unittest-parallel -k name 'Craig A. Hobbs' -k email 'craigahobbs@gmail.com' -k github 'craigahobbs' -k noapi 1
~~~
