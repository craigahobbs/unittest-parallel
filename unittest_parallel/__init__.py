# Licensed under the MIT License
# https://github.com/craigahobbs/unittest-parallel/blob/master/LICENSE

import argparse
from itertools import chain
import multiprocessing
import os
import sys
import tempfile
import unittest

try:
    import coverage
except ImportError:
    coverage = None


def main():

    # Command line parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=True,
                        help='Verbose output')
    parser.add_argument('-q', '--quiet', dest='verbose', action='store_false', default=True,
                        help='Quiet output')
    parser.add_argument('-s', '--start-directory', metavar='START', default='.',
                        help="Directory to start discovery ('.' default)")
    parser.add_argument('-p', '--pattern', metavar='PATTERN', default='test*.py',
                        help="Pattern to match tests ('test*.py' default)")
    parser.add_argument('-t', '--top-level-directory', metavar='TOP',
                        help='Top level directory of project (defaults to start directory)')
    parser.add_argument('-j', '--jobs', metavar='COUNT', type=int, default=0,
                        help='The number of test processes (default is 0, all cores)')
    parser.add_argument('--coverage', action='store_true',
                        help='Run tests with coverage.')
    parser.add_argument('--coverage-branch', action='store_true',
                        help='Run tests with branch coverage.')
    parser.add_argument('--coverage-rcfile', metavar='RCFILE',
                        help='Specify coverage configuration file.')
    parser.add_argument('--coverage-include', metavar='PAT', action='append',
                        help='Include only files matching one of these patterns. Accepts shell-style wildcards, which must be quoted.')
    parser.add_argument('--coverage-omit', metavar='PAT', action='append',
                        help='Omit files matching one of these patterns. Accepts shell-style wildcards, which must be quoted.')
    parser.add_argument('--coverage-source', metavar='SRC', action='append',
                        help='A list of packages or directories of code to be measured.')
    parser.add_argument('--coverage-html', metavar='DIR',
                        help='Generate coverage HTML report.')
    parser.add_argument('--coverage-fail-under', metavar='MIN', type=int,
                        help='Fail if coverage percentage under min.')
    args = parser.parse_args()
    if args.coverage_branch:
        args.coverage = args.coverage_branch

    process_count = max(0, args.jobs)
    if process_count == 0:
        process_count = multiprocessing.cpu_count()

    # Create the temporary directory (for coverage files)
    with tempfile.TemporaryDirectory() as temp_dir:

        # Discover tests
        cov = _coverage_start(args, temp_dir)
        try:
            test_loader = unittest.TestLoader()
            test_suites = test_loader.discover(args.start_directory, pattern=args.pattern, top_level_dir=args.top_level_directory)
        finally:
            _coverage_end(cov, args)

        # Run the tests in parallel
        pool = multiprocessing.Pool(process_count)
        results = pool.map(
            _runtest,
            ((test_suite, args, temp_dir) for test_suite in test_suites if test_suite.countTestCases() > 0)
        )

        # Test report
        run_count = sum(run for run, _, _ in results)
        error_count = sum(len(errors) for _, errors, _ in results)
        failure_count = sum(len(failures) for _, _, failures in results)
        print()
        print('Ran {0} tests'.format(run_count))
        if error_count or failure_count:
            print()
            print()
            if error_count > 0:
                print('ERRORS: {0}'.format(error_count))
            if failure_count > 0:
                print('FAILURES: {0}'.format(failure_count))
            print()
            for error_text in chain.from_iterable(errors for _, errors, _ in results):
                print(error_text)
            for failure_text in chain.from_iterable(failures for _, _, failures in results):
                print(failure_text)
            sys.exit(error_count + failure_count)

        if args.coverage and coverage:

            # Combine the coverage files
            cov = coverage.Coverage(config_file=args.coverage_rcfile)
            cov.combine(data_paths=[os.path.join(temp_dir, x) for x in os.listdir(temp_dir)])

            # HTML coverage report
            if args.coverage_html:
                cov.html_report(directory=args.coverage_html, ignore_errors=True)

            # Coverage report
            print()
            percent_covered = cov.report(ignore_errors=True)

            # Fail under
            if args.coverage_fail_under and percent_covered < args.coverage_fail_under:
                sys.exit(2)


def _format_error(result, error):
    return '\n'.join([
        '=' * 40,
        result.getDescription(error[0]),
        '-' * 40,
        error[1]
    ])

def _coverage_start(args, temp_dir):
    cov = None
    if args.coverage and coverage:
        with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False) as coverage_file:
            pass
        cov = coverage.Coverage(
            config_file=args.coverage_rcfile,
            data_file=coverage_file.name,
            branch=args.coverage_branch,
            include=args.coverage_include,
            omit=chain(args.coverage_omit if args.coverage_omit else [], [__file__]),
            source=args.coverage_source
        )
        cov.start()
    return cov

def _coverage_end(cov, args):
    if args.coverage and coverage:
        cov.stop()
        cov.save()

def _runtest(pool_args):
    test_suite, args, temp_dir = pool_args

    cov = _coverage_start(args, temp_dir)
    try:
        # Run the test suite
        runner = unittest.TextTestRunner(verbosity=(2 if args.verbose else 1))
        result = runner.run(test_suite)

        return (
            result.testsRun,
            [_format_error(result, error) for error in result.errors],
            [_format_error(result, failure) for failure in result.failures]
        )
    finally:
        _coverage_end(cov, args)
