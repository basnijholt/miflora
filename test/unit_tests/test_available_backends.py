"""Tests for miflora.available_backends."""
import unittest
from unittest import mock
from miflora import available_backends, BluepyBackend, GatttoolBackend, PygattBackend


class TestAvailableBackends(unittest.TestCase):
    """Tests for miflora.available_backends."""

    @mock.patch('miflora.backends.gatttool.call', return_value=None)
    def test_all(self, _):
        """Tests with all backends available.

        bluepy is installed via tox, gatttool is mocked.
        """
        backends = available_backends()
        self.assertEqual(3, len(backends))
        self.assertIn(BluepyBackend, backends)
        self.assertIn(GatttoolBackend, backends)
        self.assertIn(PygattBackend, backends)

    @mock.patch('miflora.backends.gatttool.call', **{'side_effect': IOError()})
    def test_one_missing(self, _):
        """Tests with all backends available.

        bluepy is installed via tox, gatttool is mocked.
        """
        backends = available_backends()
        self.assertEqual(2, len(backends))
        self.assertIn(BluepyBackend, backends)
        self.assertIn(PygattBackend, backends)
