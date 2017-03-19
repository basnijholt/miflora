""""
Read data from Mi Flora plant sensor.

Reading from the sensor is handled by the command line tool "gatttool" that
is part of bluez on Linux.
No other operating systems are supported at the moment
"""

from datetime import datetime, timedelta
from threading import Lock
import logging
import time
from bluepy.btle import Peripheral, BTLEException

MI_TEMPERATURE = "temperature"
MI_LIGHT = "light"
MI_MOISTURE = "moisture"
MI_CONDUCTIVITY = "conductivity"
MI_BATTERY = "battery"

BYTEORDER = 'little'
INVALID_DATA = b'\xaa\xbb\xcc\xdd\xee\xff\x99\x88wf\x00\x00\x00\x00\x00\x00'

LOGGER = logging.getLogger(__name__)

LOCK = Lock()


class MiFloraPoller(object):
    """"
    A class to read data from Mi Flora plant sensors.
    """

    def __init__(self, mac, cache_timeout=600, retries=3, adapter='hci0'):
        """
        Initialize a Mi Flora Poller for the given MAC address.
        """
        # TODO: the lifecycle of peripheral is a bit strange and might need improvement
        self.peripheral = None
        self._mac = mac
        self._adapter = adapter
        self._cache = None
        self._cache_timeout = timedelta(seconds=cache_timeout)
        self._last_read = None
        self._fw_last_read = datetime.now()
        self.retries = retries
        self.ble_timeout = 10
        self.lock = Lock()
        self._firmware_version = None

    def name(self):
        """
        Return the name of the sensor.
        """
        self._connect()
        byte_array = self._retry(self.peripheral.readCharacteristic, [0x03])
        return byte_array.decode('ascii')

    def fill_cache(self):
        firmware_version = self.firmware_version()
        if not firmware_version:
            # If a sensor doesn't work, wait 5 minutes before retrying
            self._last_read = datetime.now() - self._cache_timeout + \
                timedelta(seconds=300)
            return

        if firmware_version >= "2.6.6":
            self._retry(self.peripheral.writeCharacteristic, [0x33, bytes([0xA0, 0x1F]), True])
        result = self._retry(self.peripheral.readCharacteristic, [0x35])
        LOGGER.debug('Raw data for char 0x35: %s', self._format_bytes(result))

        if result != INVALID_DATA:
            self._last_read = datetime.now()
            self._decode_characteristic_35(result)
            self._disconnect()
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

    def _connect(self):
        if self.peripheral is None:
            self.peripheral = self._retry(Peripheral, [self._mac])
            LOGGER.debug('connected to device %s', self._mac)

    def _disconnect(self):
        self.peripheral.disconnect()
        self.peripheral = None

    def firmware_version(self):
        """ Return the firmware version. """
        if (self._firmware_version is None) or \
                (datetime.now() - timedelta(hours=24) > self._fw_last_read):
            self._fw_last_read = datetime.now()
            self._connect()
            result = self._retry(self.peripheral.readCharacteristic, [0x38])
            self._decode_characteristic_38(result)
        return self._firmware_version

    def _decode_characteristic_38(self, byte_array):
        """Perform byte magic when decoding the data from the sensor."""
        self.battery = int.from_bytes(byte_array[0:1], byteorder=BYTEORDER)
        self._firmware_version = byte_array[2:7].decode('ascii')
        LOGGER.debug('Raw data for char 0x38: %s', self._format_bytes(byte_array))
        LOGGER.debug('battery: %d', self.battery)
        LOGGER.debug('version: %s', self._firmware_version)

    def _decode_characteristic_35(self, result):
        """Perform byte magic when decoding the data from the sensor."""
        # negative numbers are stored in one's complement
        temp_bytes = result[0:2]
        if temp_bytes[1] & 0x80 > 0:
            temp_bytes = [temp_bytes[0] ^ 0xFF, temp_bytes[1] ^ 0xFF]

        # the temperature needs to be scaled by factor of 0.1
        self._temperature = int.from_bytes(temp_bytes, byteorder=BYTEORDER)/10.0
        self._brightness = int.from_bytes(result[3:5], byteorder=BYTEORDER)
        self._moisture = int.from_bytes(result[7:8], byteorder=BYTEORDER)
        self._conductivity = int.from_bytes(result[8:10], byteorder=BYTEORDER)

        LOGGER.debug('temp: %f', self._temperature)
        LOGGER.debug('brightness: %d', self._brightness)
        LOGGER.debug('conductivity: %d', self._conductivity)
        LOGGER.debug('moisture: %d', self._moisture)

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
            if parameter == MI_CONDUCTIVITY:
                return self._conductivity
            elif parameter == MI_MOISTURE:
                return self._moisture
            elif parameter == MI_TEMPERATURE:
                return self._temperature
            elif parameter == MI_LIGHT:
                return self._brightness
            raise Exception('unknown parameter %s', parameter)

    @staticmethod
    def _retry(func, args, num_tries=5, sleep_time=0.5):
        """Retry calling a function on Exception."""
        for i in range(0, num_tries):
            try:
                return func(*args)
            except BTLEException as exception:
                LOGGER.info("function %s failed (try %d of %d)", func, i+1, num_tries)
                time.sleep(sleep_time * (2 ^ i))
                if i == num_tries - 1:
                    LOGGER.error('retry finally failed!')
                    raise exception
                else:
                    continue

    @staticmethod
    def _format_bytes(raw_data):
        """Prettyprint a byte array."""
        return ' '.join([format(c, "02x") for c in raw_data])
