""""
Read data from Mi Flora plant sensor.

Reading from the sensor is handled by the command line tool "gatttool" that
is part of bluez on Linux.
No other operating systems are supported at the moment
"""

from datetime import datetime, timedelta
from threading import Lock, current_thread
import re
from subprocess import PIPE, Popen, TimeoutExpired
import logging
import time
import signal
import os

#from gattlib import GATTRequester

MI_TEMPERATURE = "temperature"
MI_LIGHT = "light"
MI_MOISTURE = "moisture"
MI_CONDUCTIVITY = "conductivity"
MI_BATTERY = "battery"

LOGGER = logging.getLogger(__name__)

LOCK = Lock()


def write_ble(mac, handle, value, retries=3, timeout=20):
    """
    Read from a BLE address

    @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
    @param: handle - BLE characteristics handle in format 0xXX
    @param: value - value to write to the given handle
    @param: timeout - timeout in seconds
    """

    global LOCK
    attempt = 0
    delay = 10
    LOGGER.debug("Enter read_ble (%s)", current_thread())

    while attempt <= retries:
        cmd = "gatttool --device={} --char-write-req -a {} -n {}".format(mac,
                                                                         handle,
                                                                         value)
        with LOCK:
            LOGGER.debug("Created lock in thread %s",
                         current_thread())
            LOGGER.debug("Running gatttool with a timeout of %s",
                         timeout)

            with Popen(cmd,
                       shell=True,
                       stdout=PIPE,
                       preexec_fn=os.setsid) as process:
                try:
                    result = process.communicate(timeout=timeout)[0]
                    LOGGER.debug("Finished gatttool")
                except TimeoutExpired:
                    # send signal to the process group
                    os.killpg(process.pid, signal.SIGINT)
                    result = process.communicate()[0]
                    LOGGER.debug("Killed hanging gatttool")

        LOGGER.debug("Released lock in thread %s", current_thread())

        result = result.decode("utf-8").strip(' \n\t')
        LOGGER.debug("Got %s from gatttool", result)
        # Parse the output
        res = re.search("( [0-9a-fA-F][0-9a-fA-F])+", result)
        if res:
            LOGGER.debug(
                "Exit read_ble with result (%s)", current_thread())
            return [int(x, 16) for x in res.group(0).split()]

        attempt += 1
        LOGGER.debug("Waiting for %s seconds before retrying", delay)
        if attempt < retries:
            time.sleep(delay)
            delay *= 2

    LOGGER.debug("Exit read_ble, no data (%s)", current_thread())
    return None


def read_ble(mac, handle, retries=3, timeout=20):
    """
    Read from a BLE address

    @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
    @param: handle - BLE characteristics handle in format 0xXX
    @param: timeout - timeout in seconds
    """

    global LOCK
    attempt = 0
    delay = 10
    LOGGER.debug("Enter read_ble (%s)", current_thread())

    while attempt <= retries:
        cmd = "gatttool --device={} --char-read -a {}".format(mac, handle)
        with LOCK:
            LOGGER.debug("Created lock in thread %s",
                         current_thread())
            LOGGER.debug("Running gatttool with a timeout of %s",
                         timeout)

            with Popen(cmd,
                       shell=True,
                       stdout=PIPE,
                       preexec_fn=os.setsid) as process:
                try:
                    result = process.communicate(timeout=timeout)[0]
                    LOGGER.debug("Finished gatttool")
                except TimeoutExpired:
                    # send signal to the process group
                    os.killpg(process.pid, signal.SIGINT)
                    result = process.communicate()[0]
                    LOGGER.debug("Killed hanging gatttool")

        LOGGER.debug("Released lock in thread %s", current_thread())

        result = result.decode("utf-8").strip(' \n\t')
        LOGGER.debug("Got %s from gatttool", result)
        # Parse the output
        res = re.search("( [0-9a-fA-F][0-9a-fA-F])+", result)
        if res:
            LOGGER.debug(
                "Exit read_ble with result (%s)", current_thread())
            return [int(x, 16) for x in res.group(0).split()]

        attempt += 1
        LOGGER.debug("Waiting for %s seconds before retrying", delay)
        if attempt < retries:
            time.sleep(delay)
            delay *= 2

    LOGGER.debug("Exit read_ble, no data (%s)", current_thread())
    return None


class MiFloraPoller(object):
    """"
    A class to read data from Mi Flora plant sensors.
    """

    def __init__(self, mac, cache_timeout=600, retries=3):
        """
        Initialize a Mi Flora Poller for the given MAC address.
        """

        self._mac = mac
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
        name = read_ble(self._mac, "0x03",
                        retries=self.retries,
                        timeout=self.ble_timeout)
        return ''.join(chr(n) for n in name)

    def fill_cache(self):
        firmware_version = self.firmware_version()
        if not firmware_version:
            # If a sensor doesn't work, wait 5 minutes before retrying
            self._last_read = datetime.now() - self._cache_timeout + \
                timedelta(seconds=300)
            return

        if firmware_version >= "2.6.6":
            write_ble(self._mac, "0x33", "A01F")
        self._cache = read_ble(self._mac,
                               "0x35",
                               retries=self.retries,
                               timeout=self.ble_timeout)
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
            res = read_ble(self._mac, '0x038', retries=self.retries)
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
            raise IOError("Could not read data from Mi Flora sensor %s",
                          self._mac)

    def _check_data(self):
        if self._cache is None:
            return
        datasum = 0
        for i in self._cache:
            datasum += i
        if datasum == 0:
            self._cache = None

    def _parse_data(self):
        data = self._cache
        res = {}
        res[MI_TEMPERATURE] = float(data[1] * 256 + data[0]) / 10
        res[MI_MOISTURE] = data[7]
        res[MI_LIGHT] = data[4] * 256 + data[3]
        res[MI_CONDUCTIVITY] = data[9] * 256 + data[8]
        return res
