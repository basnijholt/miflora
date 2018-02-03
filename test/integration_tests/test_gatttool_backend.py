"""Test GatttoolBackend with real sensor."""
import unittest
from test import HANDLE_READ_NAME, HANDLE_WRITE_MODE_CHANGE, DATA_MODE_CHANGE, TEST_MAC
import pytest
from miflora.backends import BluetoothBackendException
from miflora.backends.gatttool import GatttoolBackend


class TestGatttoolBackend(unittest.TestCase):
    """Test GatttoolBackend with real sensor."""
    # pylint does not understand pytest fixtures, so we have to disable the warning
    # pylint: disable=no-member

    def setUp(self):
        """Setup of the test case."""
        self.backend = GatttoolBackend(retries=0, timeout=20)

    @pytest.mark.usefixtures("mac")
    def test_read(self):
        """Test reading a handle from the sensor."""
        self.backend.connect(self.mac)
        result = self.backend.read_handle(HANDLE_READ_NAME)
        self.assertIsNotNone(result)
        self.backend.disconnect()

    @pytest.mark.usefixtures("mac")
    def test_write(self):
        """Test writing data to handle of the sensor."""
        self.backend.connect(self.mac)
        result = self.backend.write_handle(HANDLE_WRITE_MODE_CHANGE, DATA_MODE_CHANGE)
        self.assertIsNotNone(result)
        self.backend.disconnect()

    def test_read_not_connected(self):
        """Test error handling if not connected."""
        with self.assertRaises(BluetoothBackendException):
            self.backend.read_handle(HANDLE_READ_NAME)

    def test_check_backend(self):
        """Test check_backend function."""
        self.assertTrue(self.backend.check_backend())

    def test_invalid_mac_exception(self):
        """Test writing data to handle of the sensor."""
        with self.assertRaises(BluetoothBackendException):
            self.backend.connect(TEST_MAC)
            self.backend.read_handle(HANDLE_READ_NAME)
