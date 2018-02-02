"""These tests check what happens if not of the bluetooth libraries are installed."""
import unittest
from miflora import BluepyBackend, GatttoolBackend, PygattBackend


class TestNoImports(unittest.TestCase):

    def test_bluepy_check(self):
        self.assertFalse(BluepyBackend.check_backend())

    def test_pygatt_check(self):
        self.assertFalse(PygattBackend.check_backend())
