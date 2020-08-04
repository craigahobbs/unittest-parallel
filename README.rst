unittest-parallel
=================

.. |badge-status| image:: https://img.shields.io/pypi/status/unittest-parallel?style=for-the-badge
   :alt: PyPI - Status
   :target: https://pypi.python.org/pypi/unittest-parallel/

.. |badge-version| image:: https://img.shields.io/pypi/v/unittest-parallel?style=for-the-badge
   :alt: PyPI
   :target: https://pypi.python.org/pypi/unittest-parallel/

.. |badge-travis| image:: https://img.shields.io/travis/craigahobbs/unittest-parallel?style=for-the-badge
   :alt: Travis (.org)
   :target: https://travis-ci.org/craigahobbs/unittest-parallel

.. |badge-codecov| image:: https://img.shields.io/codecov/c/github/craigahobbs/unittest-parallel?style=for-the-badge
   :alt: Codecov
   :target: https://codecov.io/gh/craigahobbs/unittest-parallel

.. |badge-license| image:: https://img.shields.io/github/license/craigahobbs/unittest-parallel?style=for-the-badge
   :alt: GitHub
   :target: https://github.com/craigahobbs/unittest-parallel/blob/master/LICENSE

.. |badge-python| image:: https://img.shields.io/pypi/pyversions/unittest-parallel?style=for-the-badge
   :alt: PyPI - Python Version
   :target: https://www.python.org/downloads/

|badge-status| |badge-version|

|badge-travis| |badge-codecov|

|badge-license| |badge-python|

unittest_parallel is a parallel unittest runner for Python with coverage support.

To run unittest-parallel, specify the directory containing your unit tests with the "-s" argument and
your package's top-level directory using the "-t" argument:

::

   unittest-parallel -t . -s tests

By default, unittest-parallel runs unit tests on all CPU cores available.

To run your unit tests with coverage add either the "--coverage" option (for line coverage) or the
"--coverage-branch" for line and branch coverage.

::

   unittest-parallel -t . -s tests --coverage-branch

The `coverage <https://pypi.org/project/coverage/>`_ module is required for coverage support.


Links
-----

- `Package on pypi <https://pypi.org/project/unittest-parallel/>`_
- `Source code on GitHub <https://github.com/craigahobbs/unittest-parallel>`_
- `Build on Travis CI <https://travis-ci.org/craigahobbs/unittest-parallel>`_
- `Coverage on Codecov <https://codecov.io/gh/craigahobbs/unittest-parallel>`_


Usage
-----

::

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

   unittest options:
     -s START, --start-directory START
                           Directory to start discovery ('.' default)
     -p PATTERN, --pattern PATTERN
                           Pattern to match tests ('test*.py' default)
     -t TOP, --top-level-directory TOP
                           Top level directory of project (defaults to start
                           directory)

   coverage options:
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
