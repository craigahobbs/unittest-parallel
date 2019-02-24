# Licensed under the MIT License
# https://github.com/craigahobbs/template-specialize/blob/master/LICENSE

from io import StringIO
import re
from unittest import TestCase, TestSuite
from unittest.mock import ANY, Mock, call, patch

from unittest_parallel import __version__
import unittest_parallel.__main__
from unittest_parallel.main import main


class MockMultiprocessingPool:
    def __init__(self, count):
        pass
    def map(self, func, args): # pylint: disable=no-self-use
        return [func(arg) for arg in args]


class SuccessTestCase(TestCase):
    def mock_1(self):
        pass
    def mock_2(self):
        pass
    def mock_3(self):
        pass


class FailureTestCase(TestCase):
    def mock_1(self):
        pass
    def mock_2(self):
        self.fail()
    def mock_3(self):
        pass


class ErrorTestCase(TestCase):
    def mock_1(self):
        pass
    def mock_2(self): # pylint: disable=no-self-use
        raise Exception()
    def mock_3(self):
        pass


def _create_test_suite(test_case_class):
    return TestSuite(tests=[
        TestSuite(tests=[
            test_case_class('mock_1'),
            test_case_class('mock_2'),
            test_case_class('mock_3')
        ])
    ])


class TestMain(TestCase):

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

    def test_help(self):
        with patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr:
            with self.assertRaises(SystemExit) as cm_exc:
                main(['--help'])

        self.assertEqual(cm_exc.exception.code, 0)
        self.assertEqual(stdout.getvalue(), '''\
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

Unittest options:
  -s START, --start-directory START
                        Directory to start discovery ('.' default)
  -p PATTERN, --pattern PATTERN
                        Pattern to match tests ('test*.py' default)
  -t TOP, --top-level-directory TOP
                        Top level directory of project (defaults to start
                        directory)

Coverage options:
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
''')
        self.assertEqual(stderr.getvalue(), '')

    def test_version(self):
        with patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr:
            with self.assertRaises(SystemExit) as cm_exc:
                main(['--version'])

        self.assertEqual(cm_exc.exception.code, 0)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), str(__version__) + '\n')

    def test_jobs(self):
        with patch('multiprocessing.cpu_count', Mock(return_value=1)) as cpu_count_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=TestSuite())):
            main(['-j', '1'])

        cpu_count_mock.assert_not_called()
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), '''\

Ran 0 tests
''')

    def test_pool_no_tests(self):
        with patch('multiprocessing.cpu_count', Mock(return_value=1)), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=TestSuite())):
            main([])

        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), '''\

Ran 0 tests
''')

    def test_pool_success(self):
        with patch('multiprocessing.cpu_count', Mock(return_value=1)), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(SuccessTestCase))):
            main([])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\

Ran 3 tests
''')

    def test_success(self):
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(SuccessTestCase))):
            main([])

        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK

Ran 3 tests
''')

    def test_failure(self):
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(FailureTestCase))):
            with self.assertRaises(SystemExit) as cm_exc:
                main([])

        self.assertEqual(cm_exc.exception.code, 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(stderr.getvalue(), '''\
mock_1 (tests.test_main.FailureTestCase) ... ok
mock_2 (tests.test_main.FailureTestCase) ... FAIL
mock_3 (tests.test_main.FailureTestCase) ... ok

======================================================================
FAIL: mock_2 (tests.test_main.FailureTestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<FILE>", line <LINE>, in mock_2
    self.fail()
AssertionError: None

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

FAILED (failures=1)

Ran 3 tests


FAILURES: 1

========================================
mock_2 (tests.test_main.FailureTestCase)
----------------------------------------
Traceback (most recent call last):
  File "<FILE>", line <LINE>, in mock_2
    self.fail()
AssertionError: None

''')

    def test_error(self):
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(ErrorTestCase))):
            with self.assertRaises(SystemExit) as cm_exc:
                main([])

        self.assertEqual(cm_exc.exception.code, 1)
        self.assertEqual(stdout.getvalue(), '')
        self.assert_output(re.sub(r'File ".*?", line \d+', 'File "<FILE>", line <LINE>', stderr.getvalue()), '''\
mock_1 (tests.test_main.ErrorTestCase) ... ok
mock_2 (tests.test_main.ErrorTestCase) ... ERROR
mock_3 (tests.test_main.ErrorTestCase) ... ok

======================================================================
ERROR: mock_2 (tests.test_main.ErrorTestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<FILE>", line <LINE>, in mock_2
    raise Exception()
Exception

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

FAILED (errors=1)

Ran 3 tests


ERRORS: 1

========================================
mock_2 (tests.test_main.ErrorTestCase)
----------------------------------------
Traceback (most recent call last):
  File "<FILE>", line <LINE>, in mock_2
    raise Exception()
Exception

''')

    def test_run_tests_coverage(self):
        with patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(SuccessTestCase))):
            main([])

        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK

Ran 3 tests
''')

    def test_coverage(self):
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(SuccessTestCase))):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main(['--coverage'])

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
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY]),
                call().report(ignore_errors=True)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK

Ran 3 tests


Total coverage is 100.00%
''')

    def test_coverage_branch(self):
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(SuccessTestCase))):
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
                call(branch=True, config_file=None, data_file=ANY, include=None, omit=[ANY], source=None),
                call().start(),
                call().stop(),
                call().save(),
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY]),
                call().report(ignore_errors=True)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK

Ran 3 tests


Total coverage is 100.00%
''')

    def test_coverage_no_tests(self):
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=TestSuite())):
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
                call().report(ignore_errors=True)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\

Ran 0 tests


Total coverage is 100.00%
''')

    def test_coverage_html(self):
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(SuccessTestCase))):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main(['--coverage-branch', '--coverage-html', 'html_dir'])

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
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY]),
                call().report(ignore_errors=True),
                call().html_report(directory='html_dir', ignore_errors=True)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK

Ran 3 tests


Total coverage is 100.00%
''')

    def test_coverage_xml(self):
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(SuccessTestCase))):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main(['--coverage-branch', '--coverage-xml', 'xml_dir'])

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
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY]),
                call().report(ignore_errors=True),
                call().xml_report(ignore_errors=True, outfile='xml_dir')
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK

Ran 3 tests


Total coverage is 100.00%
''')

    def test_coverage_fail_under(self):
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(SuccessTestCase))):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 99.
            with self.assertRaises(SystemExit) as cm_exc:
                main(['--coverage-branch', '--coverage-fail-under', '100'])

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
                call(config_file=None),
                call().combine(data_paths=[ANY, ANY]),
                call().report(ignore_errors=True)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK

Ran 3 tests


Total coverage is 99.00%
''')

    def test_coverage_other(self):
        with patch('coverage.Coverage') as coverage_mock, \
             patch('multiprocessing.Pool', new=MockMultiprocessingPool), \
             patch('sys.stdout', StringIO()) as stdout, \
             patch('sys.stderr', StringIO()) as stderr, \
             patch('unittest.TestLoader.discover', Mock(return_value=_create_test_suite(SuccessTestCase))):
            coverage_instance = coverage_mock.return_value
            coverage_instance.report.return_value = 100.
            main([
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
                call(config_file='rcfile'),
                call().combine(data_paths=[ANY, ANY]),
                call().report(ignore_errors=True)
            ]
        )
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(re.sub(r'\d+\.\d{3}s', '<SEC>s', stderr.getvalue()), '''\
mock_1 (tests.test_main.SuccessTestCase) ... ok
mock_2 (tests.test_main.SuccessTestCase) ... ok
mock_3 (tests.test_main.SuccessTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in <SEC>s

OK

Ran 3 tests


Total coverage is 100.00%
''')
