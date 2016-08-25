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
MI_FERTILITY = "fertility"

LOGGER = logging.getLogger(__name__)


def read_ble(mac, handle, retries=3):
    """
    Read from a BLE address

    @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
    @param: handle - BLE characteristics handle in format 0xXX
    """

    def fromhex(hexstring):
        return int(hexstring, 16)

    attempt = 0
    delay = 10
    while (attempt < retries):
        try:
            cmd = "gatttool --device={} --char-read -a {}".format(mac, handle)
            result = subprocess.check_output(cmd,
                                             shell=True
                                             ).decode("utf-8").strip(' \n\t')
            LOGGER.debug("Got %s from gatttool", result)
            # Parse the output
            res = re.search("( [0-9a-fA-F][0-9a-fA-F])+", result)
            if res:
                return list(map(fromhex, res.group(0).split()))

        except subprocess.CalledProcessError as e:
            LOGGER.debug("Error %s from gatttool (%s)", e.returncode, e.output)
            pass

        attempt += 1
        LOGGER.debug("Waiting for %s seconds before retrying", delay)
        if (attempt < retries):
            time.sleep(delay)
            delay *= 2

    return None


class MiFloraPoller(object):
    """"
    A class to read data from Mi Flora plant sensors.
    """

    # Lock on class to make sure multiple MiFloraPollers do not poll in
    # parallel
    lock = Lock()

    def __init__(self, mac, cache_timeout=600):
        """
        Initialize a Mi Flora Poller for the given MAC address.
        """

        self._mac = mac
        self._cache = None
        self._cache_timeout = timedelta(seconds=cache_timeout)
        self._last_read = None

    def name(self):
        MiFloraPoller.lock.acquire()
        name = read_ble(self._mac, "0x35")
        MiFloraPoller.lock.release()
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

            MiFloraPoller.lock.acquire()
            self._cache = read_ble(self._mac, "0x35")
            print(self._cache)
            MiFloraPoller.lock.release()
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
        res[MI_FERTILITY] = data[9] * 256 + data[8]
        return res
