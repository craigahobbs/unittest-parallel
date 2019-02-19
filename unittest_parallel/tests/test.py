import unittest


class Test(unittest.TestCase):

    def test_import(self): # pylint: disable=no-self-use
        import unittest_parallel # pylint: disable=unused-import
        import unittest_parallel.main
        import unittest_parallel.__main__
