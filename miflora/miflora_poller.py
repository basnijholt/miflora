""""
Read data from Mi Flora plant sensor.

Reading from the sensor is handled by the command line tool "gatttool" that
is part of bluez on Linux.
No other operating systems are supported at the moment
"""

from datetime import datetime, timedelta
from threading import Lock
import re
import subprocess
import logging
import time

#from gattlib import GATTRequester

MI_TEMPERATURE = "temperature"
MI_LIGHT = "light"
MI_MOISTURE = "moisture"
MI_CONDUCTIVITY = "conductivity"

LOGGER = logging.getLogger(__name__)


LOCK = Lock()


def read_ble(mac, handle, retries=3, timeout=30):
    """
    Read from a BLE address

    @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
    @param: handle - BLE characteristics handle in format 0xXX
    @param: timeout - timeout in seconds
    """

    attempt = 0
    delay = 10
    while attempt < retries:
        try:
            cmd = "gatttool --device={} --char-read -a {}".format(mac, handle)
            LOCK.acquire()
            result = subprocess.check_output(cmd,
                                             shell=True,
                                             timeout=timeout)
            LOCK.release()
            result = result.decode("utf-8").strip(' \n\t')
            LOGGER.debug("Got %s from gatttool", result)
            # Parse the output
            res = re.search("( [0-9a-fA-F][0-9a-fA-F])+", result)
            if res:
                return [int(x, 16) for x in res.group(0).split()]

        except subprocess.CalledProcessError as err:
            LOGGER.debug("Error %s from gatttool (%s)",
                         err.returncode, err.output)

        attempt += 1
        LOGGER.debug("Waiting for %s seconds before retrying", delay)
        if attempt < retries:
            time.sleep(delay)
            delay *= 2

    return None


class MiFloraPoller(object):
    """"
    A class to read data from Mi Flora plant sensors.
    """

    def __init__(self, mac, cache_timeout=600):
        """
        Initialize a Mi Flora Poller for the given MAC address.
        """

        self._mac = mac
        self._cache = None
        self._cache_timeout = timedelta(seconds=cache_timeout)
        self._last_read = None

    def name(self):
        """
        Return the name of the sensor.
        """
        name = read_ble(self._mac, "0x03")
        return ''.join(chr(n) for n in name)

    def parameter_value(self, parameter, read_cached=True):
        """
        Return a value of one of the monitored paramaters.

        This method will try to retrieve the data from cache and only
        request it by bluetooth if no cached value is stored or the cache is
        expired.
        This behaviour can be overwritten by the "read_cached" parameter.
        """

        # Check if the cache shouldn't be used
        if (read_cached is False) or (self._cache is None) or \
                (self._last_read is None) or \
                (datetime.now() - self._cache_timeout > self._last_read):

            self._cache = read_ble(self._mac, "0x35")
            self._last_read = datetime.now()

        if self._cache and (len(self._cache) == 16):
            return self._parse_data()[parameter]
        else:
            raise IOError("Could not read data from Mi Flora sensor %s",
                          self._mac)

    def _parse_data(self):
        data = self._cache
        res = {}
        res[MI_TEMPERATURE] = float(data[1] * 256 + data[0]) / 10
        res[MI_MOISTURE] = data[7]
        res[MI_LIGHT] = data[4] * 256 + data[3]
        res[MI_CONDUCTIVITY] = data[9] * 256 + data[8]
        return res
