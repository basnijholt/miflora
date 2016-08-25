'''
Created on Aug 24, 2016

@author: matuschd
'''

from datetime import datetime, timedelta
from threading import Lock

#from gattlib import GATTRequester

MI_TEMPERATURE = "temperature"
MI_LIGHT = "light"
MI_MOISTURE = "moisture"
MI_FERTILITY = "fertility"


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

    def get_name(self):
        """
        Return the name of the sensor.

        Default name is "Flower mate"
        """
        #        req = GATTRequester(self.mac)
        req = None
        MiFloraPoller.lock.aqcuire()
        byteval = req.read_by_uuid("00002a00-0000-1000-8000-00805f9b34fb")
        MiFloraPoller.lock.release()
        return str(byteval, 'utf-8')

    def get_value(self, parameter, read_cached=True):
        """
        Return a value of one of the monitored paramaters.

        This method will try to retrieve the data from cache and only
        request it by bluetooth if no cached value is stored or the cache is
        expired.
        This behaviour can be overwritten by the "read_cached" parameter.
        """

        # Check if the cache shouldn't be used
        if read_cached is False | \
                self._cache is None | \
                self._last_read is None | \
                datetime.now() - self._cache_timeout > self._last_read:

            # TODO: read data from bluetooth

            #            req = GATTRequester(self.mac)
            req = None
            MiFloraPoller.lock.aqcuire()
            self._cache = \
                req.read_by_uuid("00001a01-0000-1000-8000-00805f9b34fb")
            MiFloraPoller.lock.release()
            self._last_read = datetime.now()

        if len(self._cache) == 16:
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
