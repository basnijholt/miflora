"""Tests for the python version check.

Tests that an execption is thrown when loading the class in Python version <3.4
"""
import unittest
import sys


class TestVersioncheck(unittest.TestCase):
    """Tests for the python version check."""
    MIN_SUPPORTED_VERSION = (3, 4)

    def test_py2(self):
        """Make sure older python versions throw an exception."""
        if sys.version_info >= self.MIN_SUPPORTED_VERSION:
            return
        try:
            import miflora  # noqa: F401 # pylint: disable=unused-variable
            self.fail('Should have thrown an exception')
        except ValueError as val_err:
            self.assertIn('version', str(val_err))

    def test_py3(self):
        """Make sure newer python versions do not throw an exception."""
        if sys.version_info < self.MIN_SUPPORTED_VERSION:
            return
        import miflora  # noqa: F401 # pylint: disable=unused-variable
