""""
Read data from Mi Flora plant sensor.
"""

from datetime import datetime, timedelta
import logging
from threading import Lock
from miflora.backends import BluetoothInterface

MI_TEMPERATURE = "temperature"
MI_LIGHT = "light"
MI_MOISTURE = "moisture"
MI_CONDUCTIVITY = "conductivity"
MI_BATTERY = "battery"

LOGGER = logging.getLogger(__name__)



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
        self._fw_last_read = datetime.now()
        self.retries = retries
        self.ble_timeout = 10
        self.lock = Lock()
        self._firmware_version = None
        self.battery = None

    def name(self):
        """
        Return the name of the sensor.
        """
        with self._bt_interface.connect(self._mac) as connection:
            name = connection.read_handle("0x03")

        if not name:
            raise IOError("Could not read data from Mi Flora sensor %s" % (self._mac))
        return ''.join(chr(n) for n in name)

    def fill_cache(self):
        firmware_version = self.firmware_version()
        with self._bt_interface.connect(self._mac) as connection:
            if not firmware_version:
                # If a sensor doesn't work, wait 5 minutes before retrying
                self._last_read = datetime.now() - self._cache_timeout + \
                    timedelta(seconds=300)
                return

            if firmware_version >= "2.6.6":
                if not connection.write_handle("0x33", "A01F"):
                    # If a sensor doesn't work, wait 5 minutes before retrying
                    self._last_read = datetime.now() - self._cache_timeout + \
                        timedelta(seconds=300)
                    return
            self._cache = connection.read_handle("0x35")
            self._check_data()
            if self._cache is not None:
                self._last_read = datetime.now()
            else:
                # If a sensor doesn't work, wait 5 minutes before retrying
                self._last_read = datetime.now() - self._cache_timeout + \
                    timedelta(seconds=300)

    def battery_level(self):
        """
        Return the battery level.

        The battery level is updated when reading the firmware version. This
        is done only once every 24h
        """
        self.firmware_version()
        return self.battery

    def firmware_version(self):
        """ Return the firmware version. """
        if (self._firmware_version is None) or \
                (datetime.now() - timedelta(hours=24) > self._fw_last_read):
            self._fw_last_read = datetime.now()
            with self._bt_interface.connect(self._mac) as connection:
                res = connection.read_handle('0x038')
            if res is None:
                self.battery = 0
                self._firmware_version = None
            else:
                self.battery = res[0]
                self._firmware_version = "".join(map(chr, res[2:]))
        return self._firmware_version

    def parameter_value(self, parameter, read_cached=True):
        """
        Return a value of one of the monitored paramaters.

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
                LOGGER.debug("Using cache (%s < %s)",
                             datetime.now() - self._last_read,
                             self._cache_timeout)

        if self._cache and (len(self._cache) == 16):
            return self._parse_data()[parameter]
        else:
            raise IOError("Could not read data from Mi Flora sensor %s" % (self._mac))

    def _check_data(self):
        if self._cache is None:
            return
        if self._cache[7] > 100: # moisture over 100 procent
            self._cache = None
            return
        if self._firmware_version >= "2.6.6":
            if sum(self._cache[10:]) == 0:
                self._cache = None
                return
        if sum(self._cache) == 0:
            self._cache = None
            return None

    def _parse_data(self):
        data = self._cache
        res = {}
        res[MI_TEMPERATURE] = float(data[1] * 256 + data[0]) / 10
        res[MI_MOISTURE] = data[7]
        res[MI_LIGHT] = data[4] * 256 + data[3]
        res[MI_CONDUCTIVITY] = data[9] * 256 + data[8]
        return res
