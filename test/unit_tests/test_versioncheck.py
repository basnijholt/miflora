import unittest
import sys


class TestVersioncheck(unittest.TestCase):

    MIN_SUPPORTED_VERSION = (3, 4)

    def test_py2(self):
        """Make sure older python versions throw an exception."""
        if sys.version_info >= self.MIN_SUPPORTED_VERSION:
            return
        try:
            import miflora  # noqa: F401
            self.fail('Should have thrown an exception')
        except ValueError as e:
            self.assertIn('version', str(e))

    def test_py3(self):
        """Make sure newer python versions do not throw an exception."""
        if sys.version_info < self.MIN_SUPPORTED_VERSION:
            return
        import miflora  # noqa: F401
