"""Tests for the miflora_poller module."""
import unittest
from test.mitemp_mock_backend import MiTempMockBackend, ConnectExceptionBackend, RWExceptionBackend

from miflora import BluetoothBackendException
from miflora.mitemp_poller import MiTempPoller, MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY


class TestMiTempPoller(unittest.TestCase):
    """Tests for the MiTempPoller class."""

    # access to protected members is fine in testing
    # pylint: disable = protected-access

    TEST_MAC = '11:22:33:44:55:66'

    def test_format_bytes(self):
        """Test conversion of bytes to string."""
        self.assertEqual('AA BB 00', MiTempPoller._format_bytes([0xAA, 0xBB, 0x00]))

    def test_read_battery(self):
        """Test reading the battery level."""
        poller = MiTempPoller(self.TEST_MAC, MiTempMockBackend)
        backend = self._get_backend(poller)
        backend.battery_level = 50
        self.assertEqual(50, poller.battery_level())
        self.assertEqual(50, poller.parameter_value(MI_BATTERY))
        self.assertEqual(0, len(backend.written_handles))

    def test_read_version(self):
        """Test reading the version number."""
        poller = MiTempPoller(self.TEST_MAC, MiTempMockBackend)
        backend = self._get_backend(poller)
        backend.set_version('00.00.11')
        self.assertEqual('00.00.11', poller.firmware_version())
        self.assertEqual(0, len(backend.written_handles))

    def test_read_measurements(self):
        """Test reading data from new sensors.

        Here we expect some data being written to the sensor.
        """
        poller = MiTempPoller(self.TEST_MAC, MiTempMockBackend)
        backend = self._get_backend(poller)

        backend.temperature = 56.7

        self.assertAlmostEqual(backend.temperature, poller.parameter_value(MI_TEMPERATURE), delta=0.11)

    def test_name(self):
        """Check reading of the sensor name."""
        poller = MiTempPoller(self.TEST_MAC, MiTempMockBackend)
        backend = self._get_backend(poller)
        backend.name = 'my sensor name'

        self.assertEqual(backend.name, poller.name())

    def test_clear_cache(self):
        """Test with negative temperature."""
        poller = MiTempPoller(self.TEST_MAC, MiTempMockBackend)
        backend = self._get_backend(poller)

        self.assertFalse(poller.cache_available())
        backend.temperature = 1.0
        self.assertAlmostEqual(1.0, poller.parameter_value(MI_TEMPERATURE), delta=0.01)
        self.assertTrue(poller.cache_available())

        # data is taken from cache, new value is ignored
        backend.temperature = 2.0
        self.assertAlmostEqual(1.0, poller.parameter_value(MI_TEMPERATURE), delta=0.01)

        self.assertTrue(poller.cache_available())
        poller.clear_cache()
        self.assertFalse(poller.cache_available())

        backend.temperature = 3.0
        self.assertAlmostEqual(3.0, poller.parameter_value(MI_TEMPERATURE), delta=0.01)
        self.assertTrue(poller.cache_available())

    def test_no_answer_data(self):
        """Sensor returns None for handle 0x35.

        Check that this triggers the right exception.
        """
        poller = MiTempPoller(self.TEST_MAC, MiTempMockBackend)
        backend = self._get_backend(poller)
        backend.handle_0x0010_raw = None
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_TEMPERATURE)

    def test_no_answer_name(self):
        """Sensor returns None for handle 0x03.

        Check that this triggers the right exception.
        """
        poller = MiTempPoller(self.TEST_MAC, MiTempMockBackend)
        backend = self._get_backend(poller)
        backend.handle_0x03_raw = None
        with self.assertRaises(BluetoothBackendException):
            poller.name()

    def test_no_answer_firmware_version(self):
        """Sensor returns None for handle 0x03.

        Check that this triggers the right exception.
        """
        poller = MiTempPoller(self.TEST_MAC, MiTempMockBackend)
        backend = self._get_backend(poller)
        backend.handle_0x0024_raw = None
        self.assertTrue(poller.firmware_version() is None)

    def test_connect_exception(self):
        """Test reaction when getting a BluetoothBackendException."""
        poller = MiTempPoller(self.TEST_MAC, ConnectExceptionBackend, retries=0)
        with self.assertRaises(BluetoothBackendException):
            poller.firmware_version()
        with self.assertRaises(BluetoothBackendException):
            poller.name()
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_TEMPERATURE)
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_HUMIDITY)

    def test_rw_exception(self):
        """Test reaction when getting a BluetoothBackendException."""
        poller = MiTempPoller(self.TEST_MAC, RWExceptionBackend, retries=0)
        with self.assertRaises(BluetoothBackendException):
            poller.firmware_version()
        with self.assertRaises(BluetoothBackendException):
            poller.name()
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_TEMPERATURE)
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_HUMIDITY)

    @staticmethod
    def _get_backend(poller):
        """Get the backend from a MiTempPoller object."""
        return poller._bt_interface._backend
