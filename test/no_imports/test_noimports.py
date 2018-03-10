"""These tests check what happens if not of the bluetooth libraries are installed."""
import unittest
from btlewrap import BluepyBackend, PygattBackend


class TestNoImports(unittest.TestCase):
    """These tests check what happens if not of the bluetooth libraries are installed."""

    def test_bluepy_check(self):
        """Test bluepy check_backend."""
        self.assertFalse(BluepyBackend.check_backend())

    def test_pygatt_check(self):
        """Test pygatt check_backend."""
        self.assertFalse(PygattBackend.check_backend())
