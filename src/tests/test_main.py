# Licensed under the MIT License
# https://github.com/craigahobbs/template-specialize/blob/main/LICENSE

from io import StringIO
import re
import sys
import unittest
from unittest.mock import ANY, Mock, call, patch

import unittest_parallel.__main__
from unittest_parallel.main import main


class MockMultiprocessingPool:
    def __init__(self, count):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def map(func, args):
        return [func(arg) for arg in args]


class MockMultiprocessingManagerEvent:
    def __init__(self):
        self._value = False

    def set(self):
        self._value = True

    def is_set(self):
        return self._value


class MockMultiprocessingManager:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    Event = MockMultiprocessingManagerEvent


class SuccessTestCase(unittest.TestCase):
    def mock_1(self):
        self.assertIsNotNone(self)

    def mock_2(self):
        self.assertIsNotNone(self)

    def mock_3(self):
        self.assertIsNotNone(self)


class SuccessTestCase2(SuccessTestCase):
    def mock_1(self):
        self.assertIsNotNone(self)


class SuccessTestCase3(SuccessTestCase):
    def mock_1(self):
        self.assertIsNotNone(self)


class SuccessWithOutputTestCase(unittest.TestCase):
    def mock_1(self):
        self.assertIsNotNone(self)

    def mock_2(self):
        print('Hello stdout!')
        self.assertIsNotNone(self)

    def mock_3(self):
        print('Hello stderr!', file=sys.stderr)
        self.assertIsNotNone(self)


class FailureTestCase(unittest.TestCase):
    def mock_1(self):
        self.assertIsNotNone(self)

    def mock_2(self):
        self.fail()

    def mock_3(self):
        self.assertIsNotNone(self)


class ErrorTestCase(unittest.TestCase):
    def mock_1(self):
        self.assertIsNotNone(self)

    def mock_2(self):
        self.assertIsNotNone(self)
        raise Exception()

    def mock_3(self):
        self.assertIsNotNone(self)


class SkipTestCase(unittest.TestCase):
    def mock_1(self):
        self.assertIsNotNone(self)

    @unittest.skip('skip reason')
    def mock_2(self):
        pass # pragma: no cover

    def mock_3(self):
        self.assertIsNotNone(self)


class ExpectedFailureTestCase(unittest.TestCase):
    def mock_1(self):
        self.assertIsNotNone(self)

    @unittest.expectedFailure
    def mock_2(self):
        self.assertIsNone(self)

    @unittest.expectedFailure
    def mock_3(self):
        self.assertIsNotNone(self)


class TestMain(unittest.TestCase):

    def assert_output(self, actual, expected):
        self.assertEqual(
            re.sub(
                r'File ".*?", line \d+',
                'File "<FILE>", line <LINE>',
                re.sub(
                    r'\d+\.\d{3}s',
                    '<SEC>s',
                    actual
                )
            ),
            expected
        )

    def test_module_main(self):
        self.assertTrue(unittest_parallel.__main__)

    def test_jobs(self):
        with patch('multiprocessing.cpu_count', Mock(return_value=1)) as cpu_count_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=unittest.TestSuite())):
            main(['-j', '1'])

        cpu_count_mock.assert_not_called()
        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 0 test suites (0 total tests) across 1 processes

----------------------------------------------------------------------
Ran 0 test in <SEC>s

OK
''')

    def test_no_tests(self):
        with patch('multiprocessing.cpu_count', Mock(return_value=1)), \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=unittest.TestSuite())):
            main([])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 0 test suites (0 total tests) across 1 processes

----------------------------------------------------------------------
Ran 0 test in <SEC>s

OK
''')

    def test_success(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')]),
                unittest.TestSuite(tests=[SuccessTestCase2('mock_1')])
            ]),
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase3('mock_1')])
            ])
        ])
        with patch('multiprocessing.cpu_count', Mock(return_value=1)), \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-v'])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 5 test suites (5 total tests) across 1 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok
mock_1 (tests.test_main.SuccessTestCase2) ... ok
mock_1 (tests.test_main.SuccessTestCase3) ... ok

----------------------------------------------------------------------
Ran 5 tests in <SEC>s

OK
''')

    def test_success_max_suites(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')]),
            ])
        ])
        with patch('multiprocessing.cpu_count', Mock(return_value=2)), \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main([])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (3 total tests) across 2 processes
...
----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK
''')

    def test_success_class_fixtures(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')]),
                unittest.TestSuite(tests=[SuccessTestCase2('mock_1')])
            ]),
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase3('mock_1')])
            ])
        ])
        with patch('multiprocessing.cpu_count', Mock(return_value=1)), \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-v', '--class-fixtures'])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (5 total tests) across 1 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok
mock_1 (tests.test_main.SuccessTestCase2) ... ok
mock_1 (tests.test_main.SuccessTestCase3) ... ok

----------------------------------------------------------------------
Ran 5 tests in <SEC>s

OK
''')

    def test_success_module_fixtures(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')]),
                unittest.TestSuite(tests=[SuccessTestCase2('mock_1')])
            ]),
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase3('mock_1')])
            ])
        ])
        with patch('multiprocessing.cpu_count', Mock(return_value=1)), \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-v', '--module-fixtures'])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 2 test suites (5 total tests) across 1 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok
mock_1 (tests.test_main.SuccessTestCase2) ... ok
mock_1 (tests.test_main.SuccessTestCase3) ... ok

----------------------------------------------------------------------
Ran 5 tests in <SEC>s

OK
''')

    def test_success_module_fixtures_empty(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ]),
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[])
            ])
        ])
        with patch('multiprocessing.cpu_count', Mock(return_value=1)), \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-v', '--module-fixtures'])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 1 test suites (3 total tests) across 1 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK
''')

    def test_success_dots(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')]),
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main([])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (3 total tests) across 3 processes
...
----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK
''')

    def test_success_quiet(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-q'])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (3 total tests) across 3 processes
----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK
''')

    def test_success_verbose(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-q', '-v'])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK
''')

    def test_success_failfast(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[FailureTestCase('mock_1'), FailureTestCase('mock_2'), FailureTestCase('mock_3')])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            with self.assertRaises(SystemExit) as cm_exc:
                main(['-v', '-f'])

        self.assertEqual(cm_exc.exception.code, 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.FailureTestCase) ... ok
mock_2 (tests.test_main.FailureTestCase) ... FAIL

======================================================================
mock_2 (tests.test_main.FailureTestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<FILE>", line <LINE>, in mock_2
    self.fail()
AssertionError: None

----------------------------------------------------------------------
Ran 2 tests in <SEC>s

FAILED (failures=1)
''')

    def test_success_buffer(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[
                    SuccessWithOutputTestCase('mock_1'),
                    SuccessWithOutputTestCase('mock_2'),
                    SuccessWithOutputTestCase('mock_3')
                ])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-v', '-b'])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessWithOutputTestCase) ... ok
mock_2 (tests.test_main.SuccessWithOutputTestCase) ... ok
mock_3 (tests.test_main.SuccessWithOutputTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK
''')

    def test_success_buffer_off(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[
                    SuccessWithOutputTestCase('mock_1'),
                    SuccessWithOutputTestCase('mock_2'),
                    SuccessWithOutputTestCase('mock_3')
                ])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-v'])

        self.assertEqual(stdout.getvalue(), '''\
Hello stdout!
''')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessWithOutputTestCase) ... ok
mock_2 (tests.test_main.SuccessWithOutputTestCase) ... ok
Hello stderr!
mock_3 (tests.test_main.SuccessWithOutputTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK
''')

    def test_failure(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[FailureTestCase('mock_1'), FailureTestCase('mock_2'), FailureTestCase('mock_3')])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            with self.assertRaises(SystemExit) as cm_exc:
                main(['-v'])

        self.assertEqual(cm_exc.exception.code, 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.FailureTestCase) ... ok
mock_2 (tests.test_main.FailureTestCase) ... FAIL
mock_3 (tests.test_main.FailureTestCase) ... ok

======================================================================
mock_2 (tests.test_main.FailureTestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<FILE>", line <LINE>, in mock_2
    self.fail()
AssertionError: None

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

FAILED (failures=1)
''')

    def test_error(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[ErrorTestCase('mock_1'), ErrorTestCase('mock_2'), ErrorTestCase('mock_3')])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            with self.assertRaises(SystemExit) as cm_exc:
                main(['-v'])

        self.assertEqual(cm_exc.exception.code, 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(re.sub(r'File ".*?", line \d+', 'File "<FILE>", line <LINE>', stderr.getvalue()), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.ErrorTestCase) ... ok
mock_2 (tests.test_main.ErrorTestCase) ... ERROR
mock_3 (tests.test_main.ErrorTestCase) ... ok

======================================================================
mock_2 (tests.test_main.ErrorTestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<FILE>", line <LINE>, in mock_2
    raise Exception()
Exception

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

FAILED (errors=1)
''')

    def test_skipped(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SkipTestCase('mock_1'), SkipTestCase('mock_2'), SkipTestCase('mock_3')])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-v'])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SkipTestCase) ... ok
mock_2 (tests.test_main.SkipTestCase) ... skipped 'skip reason'
mock_3 (tests.test_main.SkipTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK (skipped=1)
''')

    def test_expected_failure(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[
                    ExpectedFailureTestCase('mock_1'),
                    ExpectedFailureTestCase('mock_2'),
                    ExpectedFailureTestCase('mock_3')
                ])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            with self.assertRaises(SystemExit) as cm_exc:
                main(['-v'])

        self.assertEqual(cm_exc.exception.code, 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(re.sub(r'File ".*?", line \d+', 'File "<FILE>", line <LINE>', stderr.getvalue()), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.ExpectedFailureTestCase) ... ok
mock_2 (tests.test_main.ExpectedFailureTestCase) ... expected failure
mock_3 (tests.test_main.ExpectedFailureTestCase) ... unexpected success

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

FAILED (expected failures=1, unexpected successes=1)
''')

    def test_run_tests_coverage(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ])
        ])
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            main(['-v'])

        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK
''')

    def test_coverage(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ])
        ])
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main(['-v', '--coverage'])

        self.assertListEqual(
            coverage_mock.mock_calls,
            [
                call(branch=False, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=False, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=False, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=False, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY, ANY, ANY]),
                call().report(ignore_errors=True, file=ANY)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK


Total coverage is 100.00%
''')

    def test_coverage_branch(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ])
        ])
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main(['-v', '--coverage-branch'])

        self.assertListEqual(
            coverage_mock.mock_calls,
            [
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY, ANY, ANY]),
                call().report(ignore_errors=True, file=ANY)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK


Total coverage is 100.00%
''')

    def test_coverage_no_tests(self):
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=unittest.TestSuite())):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main(['--coverage-branch'])

        self.assertListEqual(
            coverage_mock.mock_calls,
            [
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(config_file=None),
                call().combine(data_paths=[ANY]),
                call().report(ignore_errors=True, file=ANY)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
Running 0 test suites (0 total tests) across 1 processes

----------------------------------------------------------------------
Ran 0 test in <SEC>s

OK


Total coverage is 100.00%
''')

    def test_coverage_html(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ])
        ])
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main(['-v', '--coverage-branch', '--coverage-html', 'html_dir'])

        self.assertListEqual(
            coverage_mock.mock_calls,
            [
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY, ANY, ANY]),
                call().report(ignore_errors=True, file=ANY),
                call().html_report(directory='html_dir', ignore_errors=True)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK


Total coverage is 100.00%
''')

    def test_coverage_xml(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ])
        ])
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main(['-v', '--coverage-branch', '--coverage-xml', 'xml_dir'])

        self.assertListEqual(
            coverage_mock.mock_calls,
            [
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY, ANY, ANY]),
                call().report(ignore_errors=True, file=ANY),
                call().xml_report(ignore_errors=True, outfile='xml_dir')
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK


Total coverage is 100.00%
''')

    def test_coverage_fail_under(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ])
        ])
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 99.
            with self.assertRaises(SystemExit) as cm_exc:
                main(['-v', '--coverage-branch', '--coverage-fail-under', '100'])

        self.assertEqual(cm_exc.exception.code, 2)
        self.assertListEqual(
            coverage_mock.mock_calls,
            [
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY, ANY, ANY]),
                call().report(ignore_errors=True, file=ANY)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK


Total coverage is 99.00%
''')

    def test_coverage_other(self):
        discover_suite = unittest.TestSuite(tests=[
            unittest.TestSuite(tests=[
                unittest.TestSuite(tests=[SuccessTestCase('mock_1'), SuccessTestCase('mock_2'), SuccessTestCase('mock_3')])
            ])
        ])
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('multiprocessing.Manager', new=MockMultiprocessingManager), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=discover_suite)):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main([
                '-v',
                '--coverage-branch',
                '--coverage-rcfile', 'rcfile',
                '--coverage-include', 'include*.py',
                '--coverage-omit', 'omit*.py',
                '--coverage-source', 'source*.py'
            ])

        self.assertListEqual(
            coverage_mock.mock_calls,
            [
                call(branch=True, config_file='rcfile', data_file=ANY, include=['include*.py'],
                     omit=['omit*.py', ANY], source=['source*.py']),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file='rcfile', data_file=ANY, include=['include*.py'],
                     omit=['omit*.py', ANY], source=['source*.py']),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file='rcfile', data_file=ANY, include=['include*.py'],
                     omit=['omit*.py', ANY], source=['source*.py']),
                call().start(),
                call().stop(),
                call().save(),
                call(branch=True, config_file='rcfile', data_file=ANY, include=['include*.py'],
                     omit=['omit*.py', ANY], source=['source*.py']),
                call().start(),
                call().stop(),
                call().save(),
                call(config_file='rcfile'),
                call().combine(data_paths=[ANY, ANY, ANY, ANY]),
                call().report(ignore_errors=True, file=ANY)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
Running 3 test suites (3 total tests) across 3 processes

mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK


Total coverage is 100.00%
''')
