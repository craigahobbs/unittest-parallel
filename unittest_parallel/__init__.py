# Copyright (C) 2017 Craig Hobbs
#
# Licensed under the MIT License
# https://github.com/craigahobbs/unittest-parallel/blob/master/LICENSE

import argparse
import itertools
import multiprocessing
import sys
import unittest


def main():

    # Command line parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', dest='verbose', action="store_true", default=True,
                        help='Run verbosely (default)')
    parser.add_argument('-v', '--verbose', dest='verbose', action="store_false",
                        help='Run quietly (turns verbosity off)')
    parser.add_argument('-s', dest='start_dir', metavar='directory', default='.',
                        help="Directory or dotted module name to start discovery ('.' default)")
    parser.add_argument('-p', dest='pattern', metavar='pattern', default='test*.py',
                        help="Pattern to match test files ('test*.py' default)")
    parser.add_argument('-t', dest='top_level_dir', metavar='directory',
                        help='Top level directory of project (default to start directory)')
    parser.add_argument('-j', dest='process_count', metavar='count', type=int, default=0,
                        help='The number of test processes (default is 0, all cores)')
    args = parser.parse_args()

    process_count = max(0, args.process_count)
    if process_count == 0:
        process_count = multiprocessing.cpu_count()

    # Discover tests
    test_loader = unittest.TestLoader()
    test_suites = test_loader.discover(args.start_dir, pattern=args.pattern, top_level_dir=args.top_level_dir)

    # Run the tests in parallel
    pool = multiprocessing.Pool(process_count)
    results = pool.map(_runtest, ((test_suite, args.verbose) for test_suite in test_suites if test_suite.countTestCases() > 0))

    # Report
    error_count = sum(len(result[0]) for result in results)
    failure_count = sum(len(result[1]) for result in results)
    if error_count or failure_count:
        print()
        print()
        if error_count > 0:
            print('ERRORS: {0}'.format(error_count))
        if failure_count > 0:
            print('FAILURES: {0}'.format(failure_count))
        print()
        for error_text in itertools.chain.from_iterable(result[0] for result in results):
            print(error_text)
        for failure_text in itertools.chain.from_iterable(result[1] for result in results):
            print(failure_text)

    return error_count + failure_count


def _format_error(result, error):
    return '\n'.join([
        '=' * 40,
        result.getDescription(error[0]),
        '-' * 40,
        error[1]
    ])

def _runtest(args):
    test_suite, verbose = args
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(test_suite)
    return ([_format_error(result, error) for error in result.errors],
            [_format_error(result, failure) for failure in result.failures])
