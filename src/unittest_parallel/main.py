# Licensed under the MIT License
# https://github.com/craigahobbs/unittest-parallel/blob/main/LICENSE

import argparse
from contextlib import contextmanager
from io import StringIO
import multiprocessing
import os
import sys
import tempfile
import time
import unittest

import coverage

from . import __version__ as VERSION


def main(argv=None):

    # Command line parsing
    parser = argparse.ArgumentParser(prog='unittest-parallel')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_const', const=2, default=1,
                        help='Verbose output')
    parser.add_argument('-q', '--quiet', dest='verbose', action='store_const', const=0, default=1,
                        help='Quiet output')
    parser.add_argument('-b', '--buffer', action='store_true', default=False,
                        help='Buffer stdout and stderr during tests')
    parser.add_argument('-j', '--jobs', metavar='COUNT', type=int, default=0,
                        help='The number of test processes (default is 0, all cores)')
    parser.add_argument('--version', action='store_true',
                        help='show version number and quit')
    group_unittest = parser.add_argument_group('unittest options')
    group_unittest.add_argument('-s', '--start-directory', metavar='START', default='.',
                                help="Directory to start discovery ('.' default)")
    group_unittest.add_argument('-p', '--pattern', metavar='PATTERN', default='test*.py',
                                help="Pattern to match tests ('test*.py' default)")
    group_unittest.add_argument('-t', '--top-level-directory', metavar='TOP',
                                help='Top level directory of project (defaults to start directory)')
    group_coverage = parser.add_argument_group('coverage options')
    group_coverage.add_argument('--coverage', action='store_true',
                                help='Run tests with coverage')
    group_coverage.add_argument('--coverage-branch', action='store_true',
                                help='Run tests with branch coverage')
    group_coverage.add_argument('--coverage-rcfile', metavar='RCFILE',
                                help='Specify coverage configuration file')
    group_coverage.add_argument('--coverage-include', metavar='PAT', action='append',
                                help='Include only files matching one of these patterns. Accepts shell-style (quoted) wildcards.')
    group_coverage.add_argument('--coverage-omit', metavar='PAT', action='append',
                                help='Omit files matching one of these patterns. Accepts shell-style (quoted) wildcards.')
    group_coverage.add_argument('--coverage-source', metavar='SRC', action='append',
                                help='A list of packages or directories of code to be measured')
    group_coverage.add_argument('--coverage-html', metavar='DIR',
                                help='Generate coverage HTML report')
    group_coverage.add_argument('--coverage-xml', metavar='FILE',
                                help='Generate coverage XML report')
    group_coverage.add_argument('--coverage-fail-under', metavar='MIN', type=float,
                                help='Fail if coverage percentage under min')
    args = parser.parse_args(args=argv)
    if args.version:
        parser.exit(message=VERSION + '\n')
    if args.coverage_branch:
        args.coverage = args.coverage_branch

    process_count = max(0, args.jobs)
    if process_count == 0:
        process_count = multiprocessing.cpu_count()

    # Create the temporary directory (for coverage files)
    with tempfile.TemporaryDirectory() as temp_dir:

        # Discover tests
        with _coverage(args, temp_dir):
            test_loader = unittest.TestLoader()
            test_suites = test_loader.discover(args.start_directory, pattern=args.pattern, top_level_dir=args.top_level_directory)

        # Run the tests in parallel
        start_time = time.perf_counter()
        with multiprocessing.Pool(process_count) as pool:
            results = pool.map(
                _run_tests,
                ((test_suite, args, temp_dir) for test_suite in test_suites if test_suite.countTestCases() > 0)
            )
        stop_time = time.perf_counter()
        test_duration = stop_time - start_time

        # Aggregate parallel test run results
        tests_run = 0
        errors = []
        failures = []
        skipped = 0
        expected_failures = 0
        unexpected_successes = 0
        for result in results:
            tests_run += result[0]
            errors.extend(result[1])
            failures.extend(result[2])
            skipped += result[3]
            expected_failures += result[4]
            unexpected_successes += result[5]
        is_success = not(errors or failures or unexpected_successes)

        # Report test errors
        for error in errors:
            sys.stderr.write('\n')
            sys.stderr.write(error)
        for failure in failures:
            sys.stderr.write('\n')
            sys.stderr.write(failure)

        # Compute test info
        infos = []
        if failures:
            infos.append('failures={0}'.format(len(failures)))
        if errors:
            infos.append('errors={0}'.format(len(errors)))
        if skipped:
            infos.append('skipped={0}'.format(skipped))
        if expected_failures:
            infos.append('expected failures={0}'.format(expected_failures))
        if unexpected_successes:
            infos.append('unexpected successes={0}'.format(unexpected_successes))

        # Test report
        if args.verbose > 0:
            sys.stderr.write('\n')
        sys.stderr.write(unittest.TextTestResult.separator2)
        sys.stderr.write('\nRan {0} {1} in {2:.3f}s\n'.format(tests_run, 'tests' if tests_run > 1 else 'test', test_duration))
        if is_success:
            sys.stderr.write('\nOK')
        else:
            sys.stderr.write('\nFAILED')
        if infos:
            sys.stderr.write(' ({0})'.format(', '.join(infos)))
        sys.stderr.write('\n')

        # Return an error status on failure
        if not is_success:
            parser.exit(status=len(errors) + len(failures) + unexpected_successes)

        # Coverage?
        if args.coverage:

            # Combine the coverage files
            cov = coverage.Coverage(config_file=args.coverage_rcfile)
            cov.combine(data_paths=[os.path.join(temp_dir, x) for x in os.listdir(temp_dir)])

            # Coverage report
            percent_covered = cov.report(ignore_errors=True)
            sys.stderr.write('\nTotal coverage is {0:.2f}%\n'.format(percent_covered))

            # HTML coverage report
            if args.coverage_html:
                cov.html_report(directory=args.coverage_html, ignore_errors=True)

            # XML coverage report
            if args.coverage_xml:
                cov.xml_report(outfile=args.coverage_xml, ignore_errors=True)

            # Fail under
            if args.coverage_fail_under and percent_covered < args.coverage_fail_under:
                parser.exit(status=2)


@contextmanager
def _coverage(args, temp_dir):
    # Running tests with coverage?
    if args.coverage:
        # Generate a random coverage data file name - file is deleted along with containing directory
        with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False) as coverage_file:
            pass

        # Create the coverage object
        cov = coverage.Coverage(
            config_file=args.coverage_rcfile,
            data_file=coverage_file.name,
            branch=args.coverage_branch,
            include=args.coverage_include,
            omit=list((args.coverage_omit if args.coverage_omit else []) + [__file__]),
            source=args.coverage_source
        )
        try:
            # Start measuring code coverage
            cov.start()

            # Yield for unit test running
            yield cov
        finally:
            # Stop measuring code coverage
            cov.stop()

            # Save the collected coverage data to the data file
            cov.save()
    else:
        # Not running tests with coverage - yield for unit test running
        yield None


class ParallelTextTestResult(unittest.TextTestResult):

    def __init__(self, stream, descriptions, verbosity):
        stream = type(stream)(sys.stderr)
        super().__init__(stream, descriptions, verbosity)

    def startTest(self, test):
        # pylint: disable=bad-super-call
        super(unittest.TextTestResult, self).startTest(test)

    def _add_helper(self, test, dots_message, show_all_message):
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.write(" ... ")
            self.stream.writeln(show_all_message)
        elif self.dots:
            self.stream.write(dots_message)
        self.stream.flush()

    def addSuccess(self, test):
        # pylint: disable=bad-super-call
        super(unittest.TextTestResult, self).addSuccess(test)
        self._add_helper(test, '.', 'ok')

    def addError(self, test, err):
        # pylint: disable=bad-super-call
        super(unittest.TextTestResult, self).addError(test, err)
        self._add_helper(test, 'E', 'ERROR')

    def addFailure(self, test, err):
        # pylint: disable=bad-super-call
        super(unittest.TextTestResult, self).addFailure(test, err)
        self._add_helper(test, 'F', 'FAIL')

    def addSkip(self, test, reason):
        # pylint: disable=bad-super-call
        super(unittest.TextTestResult, self).addSkip(test, reason)
        self._add_helper(test, 's', 'skipped {0!r}'.format(reason))

    def addExpectedFailure(self, test, err):
        # pylint: disable=bad-super-call
        super(unittest.TextTestResult, self).addExpectedFailure(test, err)
        self._add_helper(test, 'x', 'expected failure')

    def addUnexpectedSuccess(self, test):
        # pylint: disable=bad-super-call
        super(unittest.TextTestResult, self).addUnexpectedSuccess(test)
        self._add_helper(test, 'u', 'unexpected success')

    def printErrors(self):
        pass


def _run_tests(pool_args):
    test_suite, args, temp_dir = pool_args
    with _coverage(args, temp_dir):
        runner = unittest.TextTestRunner(stream=StringIO(), resultclass=ParallelTextTestResult, verbosity=args.verbose, buffer=args.buffer)
        result = runner.run(test_suite)
        return (
            result.testsRun,
            [_format_error(result, error) for error in result.errors],
            [_format_error(result, failure) for failure in result.failures],
            len(result.skipped),
            len(result.expectedFailures),
            len(result.unexpectedSuccesses)
        )


def _format_error(result, error):
    return '\n'.join([
        unittest.TextTestResult.separator1,
        result.getDescription(error[0]),
        unittest.TextTestResult.separator2,
        error[1]
    ])
