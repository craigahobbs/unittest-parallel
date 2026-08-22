# Licensed under the MIT License
# https://github.com/craigahobbs/unittest-parallel/blob/main/LICENSE

"""
unittest-parallel command-line script main module
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import partial
import importlib
from io import StringIO
import multiprocessing
import os
import sys
import tempfile
import threading
import time
import unittest

import coverage


def main(argv=None):
    """
    unittest-parallel command-line script main entry point
    """

    # Command line arguments
    argument_parser_args = {'prog': 'unittest-parallel'}
    if sys.version_info >= (3, 14): # pragma: no cover
        argument_parser_args['color'] = False
    parser = argparse.ArgumentParser(**argument_parser_args)
    parser.add_argument('-v', '--verbose', action='store_const', const=2, default=1,
                        help='Verbose output')
    parser.add_argument('-q', '--quiet', dest='verbose', action='store_const', const=0, default=1,
                        help='Quiet output')
    parser.add_argument('-f', '--failfast', action='store_true', default=False,
                        help='Stop on first fail or error')
    parser.add_argument('-b', '--buffer', action='store_true', default=False,
                        help='Buffer stdout and stderr during tests')
    parser.add_argument('-k', dest='testNamePatterns', action='append', type=_convert_select_pattern,
                        help='Only run tests which match the given substring')
    parser.add_argument('-s', '--start-directory', metavar='START', default='.',
                        help="Directory to start discovery ('.' default)")
    parser.add_argument('-p', '--pattern', metavar='PATTERN', default='test*.py',
                        help="Pattern to match tests ('test*.py' default)")
    parser.add_argument('-t', '--top-level-directory', metavar='TOP',
                        help='Top level directory of project (defaults to start directory)')
    parser.add_argument('--runner', metavar='RUNNER',
                        help='Custom unittest runner class <module>.<class>')
    parser.add_argument('--result', metavar='RESULT',
                        help='Custom unittest result class <module>.<class>')
    group_parallel = parser.add_argument_group('parallelization options')
    group_parallel.add_argument('-j', '--jobs', metavar='COUNT', type=int, default=0,
                                help='The number of test workers (default is 0, all cores)')
    group_parallel.add_argument('--level', choices=['module', 'class', 'test'], default='module',
                                help="Set the test parallelism level (default is 'module')")
    group_parallel.add_argument('--disable-process-pooling', action='store_true', default=False,
                                help='Do not reuse processes used to run test suites')
    group_parallel.add_argument('--thread', action='store_true',
                                help='Use a thread pool for parallelization')
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
    if args.coverage_branch:
        args.coverage = True
    if args.thread and args.buffer:
        parser.error('--buffer cannot be used with --thread (unittest buffering is process-global)')

    # Determine the number of test processes
    process_count = max(0, args.jobs)
    if process_count == 0:
        process_count = multiprocessing.cpu_count()

    # Load the custom runner class (if provided)
    if args.runner is not None:
        try:
            runner_module_name, runner_class_name = args.runner.rsplit('.', 1)
        except ValueError:
            parser.error('argument --runner: expected <module>.<class>')
        runner_module = importlib.import_module(runner_module_name)
        args.runner_class = getattr(runner_module, runner_class_name)

    # Load the custom result class (if provided)
    if args.result is not None:
        try:
            result_module_name, result_class_name = args.result.rsplit('.', 1)
        except ValueError:
            parser.error('argument --result: expected <module>.<class>')
        result_module = importlib.import_module(result_module_name)
        args.result_class = getattr(result_module, result_class_name)

    # Create the temporary directory (for coverage files)
    with tempfile.TemporaryDirectory() as temp_dir:

        # Discover tests
        with _coverage(args, temp_dir):
            test_loader = unittest.TestLoader()
            if args.testNamePatterns:
                test_loader.testNamePatterns = args.testNamePatterns
            discover_suite = test_loader.discover(args.start_directory, pattern=args.pattern, top_level_dir=args.top_level_directory)

        # Get the parallelizable test suites
        if args.level == 'test':
            test_suites = list(_iter_test_cases(discover_suite))
        elif args.level == 'class':
            test_suites = list(_iter_class_suites(discover_suite))
        else: # args.level == 'module'
            test_suites = list(_iter_module_suites(discover_suite))

        # Don't use more processes than test suites
        process_count = max(1, min(len(test_suites), process_count))

        # Report test suites and workers
        print(
            f'Running {len(test_suites)} test suites ({discover_suite.countTestCases()} total tests) across {process_count} workers',
            file=sys.stderr
        )
        if args.verbose > 1:
            print(file=sys.stderr)

        # Run the tests in parallel
        start_time = time.perf_counter()
        if args.thread:
            # coverage.py's collector is one-per-process, so manage the coverage context here for thread
            with _coverage(args, temp_dir), \
                 ThreadPoolExecutor(max_workers=process_count) as executor:
                test_fn = partial(_run_tests_thread, args, threading.Event())
                results = list(executor.map(test_fn, test_suites))
        else:
            multiprocessing_context = multiprocessing.get_context(method='spawn')
            maxtasksperchild = 1 if args.disable_process_pooling else None
            failfast_event = multiprocessing_context.Event()
            with multiprocessing_context.Pool(
                    process_count,
                    initializer=_init_worker,
                    initargs=(failfast_event,),
                    maxtasksperchild=maxtasksperchild
            ) as pool:
                test_fn = partial(_run_tests_process, temp_dir, args)
                results = pool.map(test_fn, test_suites, chunksize=1)
        stop_time = time.perf_counter()
        test_duration = stop_time - start_time

        # Aggregate parallel test run results
        tests_run = 0
        errors = []
        failures = []
        skipped = 0
        expected_failures = 0
        unexpected_successes = []
        for result in results:
            tests_run += result[0]
            errors.extend(result[1])
            failures.extend(result[2])
            skipped += result[3]
            expected_failures += result[4]
            unexpected_successes.extend(result[5])
        is_success = not(errors or failures or unexpected_successes)

        # Compute test info
        infos = []
        if failures:
            infos.append(f'failures={len(failures)}')
        if errors:
            infos.append(f'errors={len(errors)}')
        if skipped:
            infos.append(f'skipped={skipped}')
        if expected_failures:
            infos.append(f'expected failures={expected_failures}')
        if unexpected_successes:
            infos.append(f'unexpected successes={len(unexpected_successes)}')

        # Report test errors (ParallelTextTestResult.printErrors is a no-op; a custom --result prints its own)
        if not args.result:
            if errors or failures or unexpected_successes:
                print(file=sys.stderr)
                for error in errors:
                    print(error, file=sys.stderr)
                for failure in failures:
                    print(failure, file=sys.stderr)
                for unexpected_success in unexpected_successes:
                    print(unexpected_success, file=sys.stderr)
            elif args.verbose > 0:
                print(file=sys.stderr)

        # Test report
        if not args.runner and not args.result:
            print(unittest.TextTestResult.separator2, file=sys.stderr)
            print(f'Ran {tests_run} {"tests" if tests_run > 1 else "test"} in {test_duration:.3f}s', file=sys.stderr)
            print(file=sys.stderr)
            print(f'{"OK" if is_success else "FAILED"}{" (" + ", ".join(infos) + ")" if infos else ""}', file=sys.stderr)

        # Coverage (always combine/report, even when tests failed)
        if args.coverage:

            # Combine the coverage files
            cov_options = {}
            if args.coverage_rcfile is not None:
                cov_options['config_file'] = args.coverage_rcfile
            cov = coverage.Coverage(**cov_options)
            cov.combine(data_paths=[os.path.join(temp_dir, x) for x in os.listdir(temp_dir)])

            # Coverage report
            print(file=sys.stderr)
            percent_covered = cov.report(ignore_errors=True, file=sys.stderr)
            print(f'Total coverage is {percent_covered:.2f}%', file=sys.stderr)

            # HTML coverage report
            if args.coverage_html:
                cov.html_report(directory=args.coverage_html, ignore_errors=True)

            # XML coverage report
            if args.coverage_xml:
                cov.xml_report(outfile=args.coverage_xml, ignore_errors=True)

            # Fail under
            if args.coverage_fail_under and percent_covered < args.coverage_fail_under:
                parser.exit(status=2)

        # Unix process status is 8-bit; cap so 256+ failures don't wrap to 0
        if not is_success:
            parser.exit(status=min(255, len(errors) + len(failures) + len(unexpected_successes)))


def _convert_select_pattern(pattern):
    if not '*' in pattern:
        return f'*{pattern}*'
    return pattern


@contextmanager
def _coverage(args, temp_dir):
    # Running tests with coverage?
    if args.coverage:
        # Generate a random coverage data file name - file is deleted along with containing directory
        with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False) as coverage_file:
            pass

        # Create the coverage object
        cov_options = {
            'branch': args.coverage_branch,
            'data_file': coverage_file.name,
            'include': args.coverage_include,
            'omit': (args.coverage_omit if args.coverage_omit else []) + [__file__],
            'source': args.coverage_source
        }
        if args.coverage_rcfile is not None:
            cov_options['config_file'] = args.coverage_rcfile
        cov = coverage.Coverage(**cov_options)
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


# Iterate module-level test suites - all top-level test suites returned from TestLoader.discover
def _iter_module_suites(test_suite):
    for module_suite in test_suite:
        if module_suite.countTestCases():
            yield module_suite


# Iterate class-level test suites - test suites that contains test cases
def _iter_class_suites(test_suite):
    has_cases = any(isinstance(suite, unittest.TestCase) for suite in test_suite)
    if has_cases:
        yield test_suite
    else:
        for suite in test_suite:
            yield from _iter_class_suites(suite)


# Iterate test cases (methods)
def _iter_test_cases(test_suite):
    if isinstance(test_suite, unittest.TestCase):
        yield test_suite
    else:
        for suite in test_suite:
            yield from _iter_test_cases(suite)


_WORKER_FAILFAST_EVENT = []


def _init_worker(failfast_event):
    _WORKER_FAILFAST_EVENT.clear()
    _WORKER_FAILFAST_EVENT.append(failfast_event)


# Process function to run a test_suite
def _run_tests_process(temp_dir, args, test_suite):
    with _coverage(args, temp_dir):
        return _run_tests_thread(args, _WORKER_FAILFAST_EVENT[0], test_suite)


# Thread function to run a test_suite
def _run_tests_thread(args, failfast_event, test_suite):
    # Fail fast?
    if failfast_event.is_set():
        return [0, [], [], 0, 0, []]

    # Run unit tests
    runner_class = unittest.TextTestRunner if not args.runner else args.runner_class
    runner_stream = StringIO() if not args.runner and not args.result else None
    result_class = args.result_class if args.result else partial(ParallelTextTestResult, failfast_event=failfast_event)
    runner = runner_class(
        stream=runner_stream,
        resultclass=result_class,
        verbosity=args.verbose,
        failfast=args.failfast,
        buffer=args.buffer
    )
    result = runner.run(test_suite)

    # Set failfast, if necessary
    if result.shouldStop:
        failfast_event.set()

    # Return (test_count, errors, failures, skipped_count, expected_failure_count, unexpected_successes)
    return (
        result.testsRun,
        [_run_tests_error(result, error) for error in result.errors],
        [_run_tests_error(result, failure) for failure in result.failures],
        len(result.skipped),
        len(result.expectedFailures),
        [_run_tests_error(result, (test, 'UNEXPECTED SUCCESS')) for test in result.unexpectedSuccesses]
    )


def _run_tests_error(result, error):
    return '\n'.join([
        unittest.TextTestResult.separator1,
        result.getDescription(error[0]),
        unittest.TextTestResult.separator2,
        error[1]
    ])


class ParallelTextTestResult(unittest.TextTestResult):

    def __init__(self, stream, descriptions, verbosity, failfast_event=None):
        stream = type(stream)(sys.stderr)
        super().__init__(stream, descriptions, verbosity)
        self._failfast_event = failfast_event

    def startTest(self, test):
        if self._failfast_event is not None and self._failfast_event.is_set():
            self.stop()
        if self.showAll:
            self.stream.writeln(f'{self.getDescription(test)} ...')
            self.stream.flush()
        super(unittest.TextTestResult, self).startTest(test)

    def stopTest(self, test):
        super().stopTest(test)
        if self._failfast_event is not None and self._failfast_event.is_set():
            self.stop()

    def _add_helper(self, test, dots_message, show_all_message):
        if self.showAll:
            self.stream.writeln(f'{self.getDescription(test)} ... {show_all_message}')
        elif self.dots:
            self.stream.write(dots_message)
        self.stream.flush()

    def addSuccess(self, test):
        super(unittest.TextTestResult, self).addSuccess(test)
        self._add_helper(test, '.', 'ok')

    def addError(self, test, err):
        super(unittest.TextTestResult, self).addError(test, err)
        self._add_helper(test, 'E', 'ERROR')

    def addFailure(self, test, err):
        super(unittest.TextTestResult, self).addFailure(test, err)
        self._add_helper(test, 'F', 'FAIL')

    def addSkip(self, test, reason):
        super(unittest.TextTestResult, self).addSkip(test, reason)
        self._add_helper(test, 's', f'skipped {reason!r}')

    def addExpectedFailure(self, test, err):
        super(unittest.TextTestResult, self).addExpectedFailure(test, err)
        self._add_helper(test, 'x', 'expected failure')

    def addUnexpectedSuccess(self, test):
        super(unittest.TextTestResult, self).addUnexpectedSuccess(test)
        self._add_helper(test, 'u', 'unexpected success')

    def printErrors(self):
        pass
