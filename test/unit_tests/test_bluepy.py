"""Unit tests for the bluepy backend."""

import unittest
from unittest import mock
from test import TEST_MAC
from bluepy.btle import BTLEException
from miflora.backends.bluepy import BluepyBackend
from miflora.backends import BluetoothBackendException


class TestBluepy(unittest.TestCase):
    """Unit tests for the bluepy backend."""

    # pylint: disable=no-self-use

    @mock.patch('bluepy.btle.Peripheral')
    def test_configuration_default(self, mock_peripheral):
        """Test adapter name pattern parsing."""
        backend = BluepyBackend()
        backend.connect(TEST_MAC)
        mock_peripheral.assert_called_with(TEST_MAC, iface=0)

    @mock.patch('bluepy.btle.Peripheral')
    def test_configuration_hci12(self, mock_peripheral):
        """Test adapter name pattern parsing."""
        backend = BluepyBackend(adapter='hci12')
        backend.connect(TEST_MAC)
        mock_peripheral.assert_called_with(TEST_MAC, iface=12)

    @mock.patch('bluepy.btle.Peripheral')
    def test_configuration_invalid(self, _):
        """Test adapter name pattern parsing."""
        backend = BluepyBackend(adapter='somestring')
        with self.assertRaises(BluetoothBackendException):
            backend.connect(TEST_MAC)

    def test_check_backend_ok(self):
        """Test check_backend successfully."""
        self.assertTrue(BluepyBackend.check_backend())

    @mock.patch('bluepy.btle.Peripheral', **{'side_effect': BTLEException(1, 'text')})
    def test_connect_exception(self, _):
        """Test exception wrapping."""
        backend = BluepyBackend()
        with self.assertRaises(BluetoothBackendException):
            backend.connect(TEST_MAC)
