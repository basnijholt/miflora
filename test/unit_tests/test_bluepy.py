"""Unit tests for the bluepy backend."""
from miflora.backends.bluepy import BluepyBackend

import unittest
from unittest import mock
from test import TEST_MAC


class TestBluepy(unittest.TestCase):
    """Unit tests for the bluepy backend."""

    @mock.patch('bluepy.btle.Peripheral')
    def test_adapter_configuration_default(self, mock_peripheral):
        be = BluepyBackend()
        be.connect(TEST_MAC)
        mock_peripheral.assert_called_with(TEST_MAC, iface=0)

    @mock.patch('bluepy.btle.Peripheral')
    def test_adapter_configuration_hci12(self, mock_peripheral):
        be = BluepyBackend(adapter='hci12')
        be.connect(TEST_MAC)
        mock_peripheral.assert_called_with(TEST_MAC, iface=12)

    @mock.patch('bluepy.btle.Peripheral')
    def test_adapter_configuration_invalid_adapter(self, _):
        be = BluepyBackend(adapter='somestring')
        with self.assertRaises(ValueError):
            be.connect(TEST_MAC)
