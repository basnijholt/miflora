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

"""Configure how long data is cached before new values are
retrieved from the sensor.
"""
UPDATE_INTERVAL = 5*60

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
        self._battery = None
        self._name = None
        self._temperature = None
        self._brightness = None
        self._moisture = None
        self._conductivity = None

    def _fetch_name(self, peripheral):
        """
        Fetch the name of the sensor.
        """
        byte_array = self._retry(peripheral.readCharacteristic, [0x03])
        self._name = byte_array.decode('ascii')

    def _fill_cache(self,read_cached=True):
        if self._last_read is None or \
               (self._last_read + timedelta(seconds=UPDATE_INTERVAL)) <= datetime.now() or \
                not read_cached:
            # TODO: pick the right adapter when creating the Peripheral
            peripheral = self._retry(Peripheral, [self._mac])
            LOGGER.debug('connected to device %s', self._mac)

            self._fetch_name(peripheral)
            self._fetch_version_battery(peripheral)
            self._fetch_measurements(peripheral)
            peripheral.disconnect()
            self._last_read = datetime.now()

    def _fetch_version_battery(self, peripheral):
        result = self._retry(peripheral.readCharacteristic, [0x38])
        self._decode_characteristic_38(result)

    def _fetch_measurements(self, peripheral):
        if self._firmware_version >= "2.6.6":
            self._retry(peripheral.writeCharacteristic, [0x33, bytes([0xA0, 0x1F]), True])
        result = self._retry(peripheral.readCharacteristic, [0x35])
        LOGGER.debug('Raw data for char 0x35: %s', self._format_bytes(result))

        if result == INVALID_DATA:
            raise Exception('Received invalid data from the sensor')
        self._decode_characteristic_35(result)

    def battery_level(self):
        self._fill_cache()
        return self._battery

    def firmware_version(self):
        """ Return the firmware version. """
        self._fill_cache()
        return self._firmware_version

    def name(self):
        return self._name

    def _decode_characteristic_38(self, byte_array):
        """Perform byte magic when decoding the data from the sensor."""
        self._battery = int.from_bytes(byte_array[0:1], byteorder=BYTEORDER)
        self._firmware_version = byte_array[2:7].decode('ascii')
        LOGGER.debug('Raw data for char 0x38: %s', self._format_bytes(byte_array))
        LOGGER.debug('battery: %d', self._battery)
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

        self._fill_cache(read_cached)
        if parameter == MI_BATTERY:
            return self.battery_level()
        elif parameter == MI_CONDUCTIVITY:
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
