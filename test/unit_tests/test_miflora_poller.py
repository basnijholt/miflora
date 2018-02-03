"""Tests for the miflora_poller module."""
import unittest
from test.helper import MockBackend, ConnectExceptionBackend, RWExceptionBackend
from test import HANDLE_WRITE_MODE_CHANGE, HANDLE_READ_SENSOR_DATA, INVALID_DATA

from miflora import BluetoothBackendException
from miflora.miflora_poller import MiFloraPoller, MI_LIGHT, MI_TEMPERATURE, MI_MOISTURE, MI_CONDUCTIVITY, MI_BATTERY


class TestMifloraPoller(unittest.TestCase):
    """Tests for the MiFloraPoller class."""

    # access to protected members is fine in testing
    # pylint: disable = protected-access

    TEST_MAC = '11:22:33:44:55:66'

    def test_format_bytes(self):
        """Test conversion of bytes to string."""
        self.assertEqual('AA BB 00', MiFloraPoller._format_bytes([0xAA, 0xBB, 0x00]))

    def test_read_battery(self):
        """Test reading the battery level."""
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)
        backend.battery_level = 50
        self.assertEqual(50, poller.battery_level())
        self.assertEqual(50, poller.parameter_value(MI_BATTERY))
        self.assertEqual(0, len(backend.written_handles))

    def test_read_version(self):
        """Test reading the version number."""
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)
        backend.set_version(1, 2, 3)
        self.assertEqual('1.2.3', poller.firmware_version())
        self.assertEqual(0, len(backend.written_handles))

    def test_read_old_version(self):
        """Test reading data from old sensors.

        Old means: version < 2.6.6
        """
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)
        backend.set_version(2, 1, 0)

        backend.temperature = 32.5
        backend.moisture = 77
        backend.conductivity = 1234
        backend.brightness = 12345

        self.assertAlmostEqual(backend.temperature, poller.parameter_value(MI_TEMPERATURE), delta=0.11)
        self.assertEqual(backend.moisture, poller.parameter_value(MI_MOISTURE))
        self.assertEqual(backend.brightness, poller.parameter_value(MI_LIGHT))
        self.assertEqual(backend.conductivity, poller.parameter_value(MI_CONDUCTIVITY))
        self.assertEqual(0, len(backend.written_handles))

    def test_read_measurements(self):
        """Test reading data from new sensors.

        Here we expect some data being written to the sensor.
        """
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)

        backend.set_version(2, 7, 6)
        backend.temperature = 56.7
        backend.expected_write_handles.add(HANDLE_WRITE_MODE_CHANGE)

        self.assertAlmostEqual(backend.temperature, poller.parameter_value(MI_TEMPERATURE), delta=0.11)
        self.assertEqual(1, len(backend.written_handles))
        self.assertEqual((HANDLE_WRITE_MODE_CHANGE, b'\xA0\x1F'), backend.written_handles[0])

    def test_invalid_data_old(self):
        """Check if reading of the data fails, when invalid data is received.

        Try this with an old version number.
        """
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)

        backend.set_version(2, 5, 0)

        backend.override_read_handles[HANDLE_READ_SENSOR_DATA] = INVALID_DATA
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_TEMPERATURE)

    def test_invalid_data_new(self):
        """Check if reading of the data fails, when invalid data is received.

        Try this with a new version number.
        """
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)

        backend.set_version(2, 7, 6)

        backend.override_read_handles[HANDLE_READ_SENSOR_DATA] = INVALID_DATA
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_TEMPERATURE)

    def test_name(self):
        """Check reading of the sensor name."""
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)
        backend.name = 'my sensor name'

        self.assertEqual(backend.name, poller.name())

    def test_negative_temperature(self):
        """Test with negative temperature."""
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)
        backend.handle_0x35_raw = bytes(b'\x53\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x02\x3C\x00\xFB\x34\x9B')
        self.assertAlmostEqual(-17.3, poller.parameter_value(MI_TEMPERATURE), delta=0.01)

    def test_clear_cache(self):
        """Test with negative temperature."""
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
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
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)
        backend.handle_0x35_raw = None
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_TEMPERATURE)

    def test_no_answer_name(self):
        """Sensor returns None for handle 0x03.

        Check that this triggers the right exception.
        """
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)
        backend.handle_0x03_raw = None
        with self.assertRaises(BluetoothBackendException):
            poller.name()

    def test_no_answer_version(self):
        """Sensor returns None for handle 0x03.

        Check that this triggers the right exception.
        """
        poller = MiFloraPoller(self.TEST_MAC, MockBackend)
        backend = self._get_backend(poller)
        backend.handle_0x38_raw = None
        with self.assertRaises(BluetoothBackendException):
            poller.name()

    def test_connect_exception(self):
        """Test reaction when getting a BluetoothBackendException."""
        poller = MiFloraPoller(self.TEST_MAC, ConnectExceptionBackend, retries=0)
        with self.assertRaises(BluetoothBackendException):
            poller.firmware_version()
        with self.assertRaises(BluetoothBackendException):
            poller.name()
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_MOISTURE)
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_MOISTURE)

    def test_rw_exception(self):
        """Test reaction when getting a BluetoothBackendException."""
        poller = MiFloraPoller(self.TEST_MAC, RWExceptionBackend, retries=0)
        with self.assertRaises(BluetoothBackendException):
            poller.firmware_version()
        with self.assertRaises(BluetoothBackendException):
            poller.name()
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_MOISTURE)
        with self.assertRaises(BluetoothBackendException):
            poller.parameter_value(MI_MOISTURE)

    @staticmethod
    def _get_backend(poller):
        """Get the backend from a MiFloraPoller object."""
        return poller._bt_interface._backend
