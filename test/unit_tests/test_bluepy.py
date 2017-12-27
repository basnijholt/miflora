"""Unit tests for the bluepy backend."""
from miflora.backends.bluepy import BluepyBackend

import unittest
from unittest import mock
from test import TEST_MAC


class TestBluepy(unittest.TestCase):
    """Unit tests for the bluepy backend."""

    @mock.patch('bluepy.btle.Peripheral')
    def test_adapter_configuration_default(self, mock_peripheral):
        """Test parsing of the adapter name."""
        backend = BluepyBackend()
        backend.connect(TEST_MAC)
        mock_peripheral.assert_called_with(TEST_MAC, iface=0)

    @mock.patch('bluepy.btle.Peripheral')
    def test_adapter_configuration_hci12(self, mock_peripheral):
        """Test parsing of the adapter name."""
        backend = BluepyBackend(adapter='hci12')
        backend.connect(TEST_MAC)
        mock_peripheral.assert_called_with(TEST_MAC, iface=12)

    @mock.patch('bluepy.btle.Peripheral')
    def test_adapter_configuration_invalid_adapter(self, _):
        """Test parsing of the adapter name."""
        backend = BluepyBackend(adapter='somestring')
        with self.assertRaises(ValueError):
            backend.connect(TEST_MAC)
