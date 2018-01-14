""""
Read data from Mi Flora plant sensor.
"""

from datetime import datetime, timedelta
import time
from struct import unpack
import logging
from threading import Lock
from miflora.backends import BluetoothInterface

_HANDLE_READ_VERSION_BATTERY = 0x38
_HANDLE_READ_NAME = 0x03
_HANDLE_READ_SENSOR_DATA = 0x35
_HANDLE_WRITE_MODE_CHANGE = 0x33
_DATA_MODE_CHANGE = bytes([0xA0, 0x1F])

MI_TEMPERATURE = "temperature"
MI_LIGHT = "light"
MI_MOISTURE = "moisture"
MI_CONDUCTIVITY = "conductivity"
MI_BATTERY = "battery"
MI_FIRMWARE = "firmware"
MI_DEVICE_TIME = "device_time"
MI_WALL_TIME = "wall_time"

_LOGGER = logging.getLogger(__name__)

BYTEORDER = 'little'

_HANDLE_DEVICE_TIME = 0x41
_HANDLE_HISTORY_CONTROL = 0x3e
_HANDLE_HISTORY_READ = 0x3c

_CMD_HISTORY_READ_INIT = b'\xa0\x00\x00'
_CMD_HISTORY_READ_SUCCESS = b'\xa2\x00\x00'
_CMD_HISTORY_READ_FAILED = b'\xa3\x00\x00'

_INVALID_HISTORY_DATA = [
    b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff',
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
]


class MiFloraPoller(object):
    """"
    A class to read data from Mi Flora plant sensors.
    """

    def __init__(self, mac, backend, cache_timeout=600, retries=3, adapter='hci0'):
        """
        Initialize a Mi Flora Poller for the given MAC address.
        """

        self._mac = mac
        self._bt_interface = BluetoothInterface(backend, adapter)
        self._cache = None
        self._cache_timeout = timedelta(seconds=cache_timeout)
        self._last_read = None
        self._fw_last_read = None
        self.retries = retries
        self.ble_timeout = 10
        self.lock = Lock()
        self._firmware_version = None
        self.battery = None

    def name(self):
        """Return the name of the sensor."""
        with self._bt_interface.connect(self._mac) as connection:
            name = connection.read_handle(_HANDLE_READ_NAME)

        if not name:
            raise IOError("Could not read data from Mi Flora sensor %s" % self._mac)
        return ''.join(chr(n) for n in name)

    def fill_cache(self):
        """Fill the cache with new data from the sensor."""
        _LOGGER.debug('Filling cache with new sensor data.')
        firmware_version = self.firmware_version()
        with self._bt_interface.connect(self._mac) as connection:
            if not firmware_version:
                # If a sensor doesn't work, wait 5 minutes before retrying
                self._last_read = datetime.now() - self._cache_timeout + \
                    timedelta(seconds=300)
                return

            if firmware_version >= "2.6.6":
                # for the newer models a magic number must be written before we can read the current data
                if not connection.write_handle(_HANDLE_WRITE_MODE_CHANGE, _DATA_MODE_CHANGE):
                    # If a sensor doesn't work, wait 5 minutes before retrying
                    self._last_read = datetime.now() - self._cache_timeout + \
                        timedelta(seconds=300)
                    return
            self._cache = connection.read_handle(_HANDLE_READ_SENSOR_DATA)
            _LOGGER.debug('Received result for handle %s: %s',
                          _HANDLE_READ_SENSOR_DATA, self.format_bytes(self._cache))
            self._check_data()
            if self.cache_available():
                self._last_read = datetime.now()
            else:
                # If a sensor doesn't work, wait 5 minutes before retrying
                self._last_read = datetime.now() - self._cache_timeout + \
                    timedelta(seconds=300)

    def battery_level(self):
        """Return the battery level.

        The battery level is updated when reading the firmware version. This
        is done only once every 24h
        """
        self.firmware_version()
        return self.battery

    def firmware_version(self):
        """Return the firmware version."""
        if (self._firmware_version is None) or \
                (datetime.now() - timedelta(hours=24) > self._fw_last_read):
            self._fw_last_read = datetime.now()
            with self._bt_interface.connect(self._mac) as connection:
                res = connection.read_handle(_HANDLE_READ_VERSION_BATTERY)
                _LOGGER.debug('Received result for handle %s: %s',
                              _HANDLE_READ_VERSION_BATTERY, self.format_bytes(res))
            if res is None:
                self.battery = 0
                self._firmware_version = None
            else:
                self.battery = res[0]
                self._firmware_version = "".join(map(chr, res[2:]))
        return self._firmware_version

    def parameter_value(self, parameter, read_cached=True):
        """Return a value of one of the monitored paramaters.

        This method will try to retrieve the data from cache and only
        request it by bluetooth if no cached value is stored or the cache is
        expired.
        This behaviour can be overwritten by the "read_cached" parameter.
        """
        # Special handling for battery attribute
        if parameter == MI_BATTERY:
            return self.battery_level()

        # Use the lock to make sure the cache isn't updated multiple times
        with self.lock:
            if (read_cached is False) or \
                    (self._last_read is None) or \
                    (datetime.now() - self._cache_timeout > self._last_read):
                self.fill_cache()
            else:
                _LOGGER.debug("Using cache (%s < %s)",
                              datetime.now() - self._last_read,
                              self._cache_timeout)

        if self.cache_available() and (len(self._cache) == 16):
            return self._parse_data()[parameter]
        else:
            raise IOError("Could not read data from Mi Flora sensor %s" % self._mac)

    def _check_data(self):
        """Ensure that the data in the cache is valid.

        If it's invalid, the cache is wiped.
        """
        if not self.cache_available():
            return
        if self._cache[7] > 100:  # moisture over 100 procent
            self.clear_cache()
            return
        if self._firmware_version >= "2.6.6":
            if sum(self._cache[10:]) == 0:
                self.clear_cache()
                return
        if sum(self._cache) == 0:
            self.clear_cache()
            return

    def clear_cache(self):
        """Manually force the cache to be cleared."""
        self._cache = None
        self._last_read = None

    def cache_available(self):
        """Check if there is data in the cache."""
        return self._cache is not None

    def _parse_data(self):
        """Parses the byte array returned by the sensor.

        The sensor returns 16 bytes in total. It's unclear what the meaning of these bytes
        is beyond what is decoded in this method.

        semantics of the data (in little endian encoding):
        bytes 0-1: temperature in 0.1 °C
        byte 2: unknown
        bytes 3-4: brightness in Lux
        bytes 5-6: unknown
        byte 7: conductivity in µS/cm
        byte 8-9: brightness in Lux
        bytes 10-15: unknown
        """
        data = self._cache
        res = dict()
        temp, res[MI_LIGHT], res[MI_MOISTURE], res[MI_CONDUCTIVITY] = \
            unpack('<hxhxxBhxxxxxx', data)
        res[MI_TEMPERATURE] = temp/10.0
        return res

    @staticmethod
    def format_bytes(raw_data):
        """Prettyprint a byte array."""
        return ' '.join([format(c, "02x") for c in raw_data]).upper()

    def fetch_history(self):
        """Fetch the historical measurements from the sensor.

        History is updated by the sensor every hour.
        """
        data = []
        with self._bt_interface.connect(self._mac) as connection:
            connection.write_handle(_HANDLE_HISTORY_CONTROL, _CMD_HISTORY_READ_INIT)
            history_info = connection.read_handle(_HANDLE_HISTORY_READ)
            _LOGGER.debug('history info raw: %s', history_info)

            history_length = int.from_bytes(history_info[0:2], BYTEORDER)
            _LOGGER.info("Getting %d measurements", history_length)
            if history_length > 0:
                for i in range(history_length):
                    payload = self._cmd_history_address(i)
                    try:
                        connection.write_handle(_HANDLE_HISTORY_CONTROL, payload)
                        response = connection.read_handle(_HANDLE_HISTORY_READ)
                        if response in _INVALID_HISTORY_DATA:
                            msg = 'Got invalid history data: {}'.format(response)
                            _LOGGER.error(msg)
                            raise ValueError(msg)
                        data.append(HistoryEntry(response))
                    except Exception as exception:
                        _LOGGER.debug("History read failed: %s", exception)
                        connection.write_handle(_HANDLE_HISTORY_CONTROL, _CMD_HISTORY_READ_FAILED)
                        raise
                    _LOGGER.info("Progress: %d of %d", i+1, history_length)

        _time = self._fetch_device_time()
        time_diff = _time[MI_WALL_TIME] - _time[MI_DEVICE_TIME]
        for entry in data:
            entry.compute_wall_time(time_diff)

        return data

    def clear_history(self):
        """Clear the device history.

        On the next fetch_history, you will only get new data.
        Note: The data is deleted from the device. There is no way to recover it!
        """
        with self._bt_interface.connect(self._mac) as connection:
            connection.write_handle(_HANDLE_HISTORY_CONTROL, _CMD_HISTORY_READ_SUCCESS)

    @staticmethod
    def _cmd_history_address(addr):
        """Calculate this history address"""
        return b'\xa1' + addr.to_bytes(2, BYTEORDER)

    def _fetch_device_time(self):
        """Fetch device time.

        The device time is in seconds.
        """
        start = time.time()
        with self._bt_interface.connect(self._mac) as connection:
            response = connection.read_handle(_HANDLE_DEVICE_TIME)
        _LOGGER.debug("device time raw: %s", response)
        wall_time = (time.time() + start) / 2
        device_time = int.from_bytes(response, BYTEORDER)
        _LOGGER.info('device time: %s local time: %s', device_time, wall_time)

        return {
            MI_DEVICE_TIME: device_time,
            MI_WALL_TIME: wall_time
        }


class HistoryEntry(object):
    """Entry in the history of the device."""

    def __init__(self, byte_array):
        self.device_time = None
        self.wall_time = None
        self.temperature = None
        self.light = None
        self.moisture = None
        self.conductivity = None
        self._decode_history(byte_array)

    def _decode_history(self, byte_array):
        """Perform byte magic when decoding history data."""
        # negative numbers are stored in one's complement
        # pylint: disable=trailing-comma-tuple

        temp_bytes = byte_array[4:6]
        if temp_bytes[1] & 0x80 > 0:
            temp_bytes = [temp_bytes[0] ^ 0xFF, temp_bytes[1] ^ 0xFF]

        (self.device_time,) = int.from_bytes(byte_array[:4], BYTEORDER),
        (self.temperature,) = int.from_bytes(temp_bytes, BYTEORDER) / 10.0,
        (self.light,) = int.from_bytes(byte_array[7:10], BYTEORDER),
        (self.moisture,) = byte_array[11],
        self.conductivity = int.from_bytes(byte_array[12:14], BYTEORDER)

        _LOGGER.debug('Raw data for char 0x3c: %s', MiFloraPoller.format_bytes(byte_array))
        _LOGGER.debug('device time: %d', self.device_time)
        _LOGGER.debug('temp: %f', self.temperature)
        _LOGGER.debug('brightness: %d', self.light)
        _LOGGER.debug('conductivity: %d', self.conductivity)
        _LOGGER.debug('moisture: %d', self.moisture)

    def compute_wall_time(self, time_diff):
        """Correct the device time to the wall time. """
        self.wall_time = datetime.fromtimestamp(self.device_time + time_diff)
