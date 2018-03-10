"""Run the same tests as in TestGatttoolBackend.

Just use a different backend.
"""
from test.integration_tests.test_gatttool_backend import TestGatttoolBackend
from test import TEST_MAC, HANDLE_READ_NAME
from btlewrap import bluepy, BluetoothBackendException


class TestBluepyBackend(TestGatttoolBackend):
    """Run the same tests as in TestGatttoolBackend.

    Just use a different backend.
    """

    def setUp(self):
        """Set up the test environment."""
        self.backend = bluepy.BluepyBackend()

    def test_scan(self):
        """Test scanning for devices.

        Note: fore the test to pass, there must be at least one BTLE device
        near by.
        """
        devices = bluepy.BluepyBackend.scan_for_devices(5)
        self.assertGreater(len(devices), 0)
        for device in devices:
            self.assertIsNotNone(device)

    def test_invalid_mac_exception(self):
        """Test writing data to handle of the sensor."""
        bluepy.RETRY_LIMIT = 1
        with self.assertRaises(BluetoothBackendException):
            self.backend.connect(TEST_MAC)
            self.backend.read_handle(HANDLE_READ_NAME)
        bluepy.RETRY_LIMIT = 3
