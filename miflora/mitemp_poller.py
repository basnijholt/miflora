""""
Read data from Mi Temp environmental (Temp and humidity) sensor.
"""

from datetime import datetime, timedelta
import logging
from threading import Lock
from miflora.backends import BluetoothInterface, BluetoothBackendException

_HANDLE_READ_BATTERY_LEVEL = 0x0018
_HANDLE_READ_FIRMWARE_VERSION = 0x0024
_HANDLE_READ_NAME = 0x03
_HANDLE_READ_WRITE_SENSOR_DATA = 0x0010


MI_TEMPERATURE = "temperature"
MI_HUMIDITY = "humidity"
MI_BATTERY = "battery"

_LOGGER = logging.getLogger(__name__)


class MiTempPoller(object):
    """"
    A class to read data from Mi Temp plant sensors.
    """

    def __init__(self, mac, backend, cache_timeout=600, retries=3, adapter='hci0'):
        """
        Initialize a Mi Temp Poller for the given MAC address.
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
            name = connection.read_handle(_HANDLE_READ_NAME)  # pylint: disable=no-member

        if not name:
            raise BluetoothBackendException("Could not read data from Mi Temp sensor %s" % self._mac)
        return ''.join(chr(n) for n in name)

    def fill_cache(self):
        """Fill the cache with new data from the sensor."""
        _LOGGER.debug('Filling cache with new sensor data.')
        try:
            self.firmware_version()
        except BluetoothBackendException:
            # If a sensor doesn't work, wait 5 minutes before retrying
            self._last_read = datetime.now() - self._cache_timeout + \
                timedelta(seconds=300)
            raise

        with self._bt_interface.connect(self._mac) as connection:
            try:
                connection.wait_for_notification(_HANDLE_READ_WRITE_SENSOR_DATA, self, 10)
                # If a sensor doesn't work, wait 5 minutes before retrying
            except BluetoothBackendException:
                self._last_read = datetime.now() - self._cache_timeout + \
                    timedelta(seconds=300)
                return

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
                res_firmware = connection.read_handle(_HANDLE_READ_FIRMWARE_VERSION)  # pylint: disable=no-member
                _LOGGER.debug('Received result for handle %s: %s',
                              _HANDLE_READ_FIRMWARE_VERSION, res_firmware)
                res_battery = connection.read_handle(_HANDLE_READ_BATTERY_LEVEL)  # pylint: disable=no-member
                _LOGGER.debug('Received result for handle %s: %d',
                              _HANDLE_READ_BATTERY_LEVEL, res_battery)

            if res_firmware is None:
                self._firmware_version = None
            else:
                self._firmware_version = res_firmware.decode("utf-8")

            if res_battery is None:
                self.battery = 0
            else:
                self.battery = int(ord(res_battery))
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

        if self.cache_available():
            return self._parse_data()[parameter]
        else:
            raise BluetoothBackendException("Could not read data from Mi Temp sensor %s" % self._mac)

    def _check_data(self):
        """Ensure that the data in the cache is valid.

        If it's invalid, the cache is wiped.
        """
        if not self.cache_available():
            return

        parsed = self._parse_data()
        _LOGGER.debug('Received new data from sensor: Temp=%.1f, Humidity=%.1f',
                      parsed[MI_TEMPERATURE], parsed[MI_HUMIDITY])

        if parsed[MI_HUMIDITY] > 100:  # humidity over 100 procent
            self.clear_cache()
            return

        if parsed[MI_TEMPERATURE] == 0:  # humidity over 100 procent
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

        The sensor returns 14 bytes in total, a readable text with the
        temperature and humidity. e.g.:

        54 3d 32 35 2e 36 20 48 3d 32 33 2e 36 00 -> T=25.6 H=23.6

        """
        data = self._cache

        res = dict()
        res[MI_HUMIDITY] = float(data[9:13])
        res[MI_TEMPERATURE] = float(data[2:6])
        return res

    @staticmethod
    def _format_bytes(raw_data):
        """Prettyprint a byte array."""
        if raw_data is None:
            return 'None'
        return ' '.join([format(c, "02x") for c in raw_data]).upper()

    def handleNotification(self, handle, raw_data):
        """ gets called by the bluepy backend when using wait_for_notification
        """
        if raw_data is None:
            return
        data = raw_data.decode("utf-8").strip(' \n\t')
        self._cache = data
        self._check_data()
        if self.cache_available():
            self._last_read = datetime.now()
        else:
            # If a sensor doesn't work, wait 5 minutes before retrying
            self._last_read = datetime.now() - self._cache_timeout + \
                timedelta(seconds=300)
