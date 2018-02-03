"""Test gatttool backend."""

import unittest
from unittest import mock
from test import TEST_MAC
from miflora import GatttoolBackend, BluetoothBackendException


class TestGatttool(unittest.TestCase):
    """Test gatttool by mocking gatttool.

    These tests do NOT require hardware!
    time.sleep is mocked in some cases to speed up the retry-feature.
    """
    # access to protected members is fine in testing
    # pylint: disable = protected-access

    # arguments of mock.patch are not always used
    # pylint: disable = unused-argument

    @mock.patch('miflora.backends.gatttool.Popen')
    def test_read_handle_ok(self, popen_mock):
        """Test reading handle successfully."""
        gattoutput = bytes([0x00, 0x11, 0xAA, 0xFF])
        _configure_popenmock(popen_mock, 'Characteristic value/descriptor: 00 11 AA FF')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        result = backend.read_handle(0xFF)
        self.assertEqual(gattoutput, result)

    def test_run_connect_disconnect(self):
        """Just run connect and disconnect"""
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        self.assertEqual(TEST_MAC, backend._mac)
        backend.disconnect()
        self.assertEqual(None, backend._mac)

    @mock.patch('miflora.backends.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_read_handle_empty_output(self, _, popen_mock):
        """Test reading handle where no result is returned."""
        _configure_popenmock(popen_mock, '')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.read_handle(0xFF)

    @mock.patch('miflora.backends.gatttool.Popen')
    def test_read_handle_wrong_handle(self, popen_mock):
        """Test reading invalid handle."""
        _configure_popenmock(popen_mock, 'Characteristic value/descriptor read failed: Invalid handle')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.read_handle(0xFF)

    def test_read_not_connected(self):
        """Test reading data when not connected."""
        backend = GatttoolBackend()
        with self.assertRaises(BluetoothBackendException):
            backend.read_handle(0xFF)

    def test_write_not_connected(self):
        """Test writing data when not connected."""
        backend = GatttoolBackend()
        with self.assertRaises(BluetoothBackendException):
            backend.write_handle(0xFF, [0x00])

    @mock.patch('miflora.backends.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_write_handle_ok(self, time_mock, popen_mock):
        """Test writing to a handle successfully."""
        _configure_popenmock(popen_mock, 'Characteristic value was written successfully')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        self.assertTrue(backend.write_handle(0xFF, b'\x00\x10\xFF'))

    @mock.patch('miflora.backends.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_write_handle_wrong_handle(self, time_mock, popen_mock):
        """Test writing to a non-writable handle."""
        _configure_popenmock(popen_mock, "Characteristic Write Request failed: Attribute can't be written")
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.write_handle(0xFF, b'\x00\x10\xFF')

    @mock.patch('miflora.backends.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_write_handle_no_answer(self, time_mock, popen_mock):
        """Test writing to a handle when no result is returned."""
        _configure_popenmock(popen_mock, '')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.write_handle(0xFF, b'\x00\x10\xFF')

    @mock.patch('miflora.backends.gatttool.call', return_value=None)
    def test_check_backend_ok(self, call_mock):
        """Test check_backend successfully."""
        self.assertTrue(GatttoolBackend().check_backend())

    @mock.patch('miflora.backends.gatttool.call', **{'side_effect': IOError()})
    def test_check_backend_fail(self, call_mock):
        """Test check_backend with IOError being risen."""
        self.assertFalse(GatttoolBackend().check_backend())


def _configure_popenmock(popen_mock, output_string):
    """Helper function to create a mock for Popen."""
    match_result = mock.Mock()
    match_result.communicate.return_value = [
        bytes(output_string, encoding='UTF-8'),
        bytes('random text', encoding='UTF-8')]
    popen_mock.return_value.__enter__.return_value = match_result
