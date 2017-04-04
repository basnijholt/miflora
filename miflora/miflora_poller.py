""""
Read data from Mi Flora plant sensor.

Reading from the sensor is handled by the command line tool "gatttool" that
is part of bluez on Linux.
No other operating systems are supported at the moment
"""
import logging
import time
import threading
from datetime import datetime
from bluepy.btle import Peripheral, BTLEException, ADDR_TYPE_PUBLIC
from miflora.decorators import retry, auto_connect, cached_ttl

LOGGER = logging.getLogger(__name__)

MI_TEMPERATURE = "temperature"
MI_LIGHT = "light"
MI_MOISTURE = "moisture"
MI_CONDUCTIVITY = "conductivity"
MI_BATTERY = "battery"
MI_FIRMWARE = "firmware"
MI_DEVICE_TIME = "device_time"
MI_WALL_TIME = "wall_time"

BYTEORDER = 'little'
INVALID_DATA = b'\xaa\xbb\xcc\xdd\xee\xff\x99\x88wf\x00\x00\x00\x00\x00\x00'

handle_device_name = 0x03
handle_device_info = 0x38
handle_device_time = 0x41
handle_measurement_control = 0x33
handle_measurement_read = 0x35
handle_history_control = 0x3e
handle_history_read = 0x3c

cmd_measurement_read_init = b'\xa0\x00'
cmd_history_read_init = b'\xa0\x00\x00'
cmd_history_read_success = b'\xa2\x00\x00'
cmd_history_read_failed = b'\xa3\x00\x00'


def cmd_history_address(addr):
    return b'\xa1' + addr.to_bytes(2, BYTEORDER)


class MiFlowerCareException(Exception):
    pass


class MiFloraPoller:
    """"
    A class to read data from Mi Flora plant sensors.
    """

    def __init__(self,
                 mac,
                 device_info_cache_ttl=3600,
                 measurement_cache_ttl=10,
                 retries=3,
                 retry_delay=lambda x: 2**(x*0.5),
                 iface=0,
                 firmware_version=None):
        """
        Initialize a Mi Flora Poller for the given MAC address.

        Arguments:
            mac (string): MAC address of the sensor to be polled
            device_info_cache_ttl (int): Maximum age of the device info data before it will be polled again
            measurement_cache_ttl (int): Maximum age of the measurement data before it will be polled again
            retries (int): number of retries for errors in the Bluetooth communication
            retry_delay (fn): delay function returning seconds of delay dependent on retry number
            iface (int): number of the Bluetooth adapter to be used, 0 means "/dev/hci0"

        """
        self._mac = mac
        self._iface = iface
        self._lock = threading.Lock()
        self._peripheral = Peripheral()
        self._firmware_version = firmware_version

        # Decorate
        retry_fcn = retry(retries, BTLEException, retry_delay, self.reconnect_on_disconnect)
        self.read = retry_fcn(self._peripheral.readCharacteristic)
        self.write = retry_fcn(self._peripheral.writeCharacteristic)
        self._fetch_device_info = cached_ttl(device_info_cache_ttl)(self._fetch_device_info)
        self._fetch_measurement = cached_ttl(measurement_cache_ttl)(self._fetch_measurement)
        self._fetch_name = cached_ttl(device_info_cache_ttl)(self._fetch_name)

    @property
    def battery_level(self):
        """Return the battery level."""
        return self._fetch_device_info()[MI_BATTERY]

    @property
    def firmware_version(self):
        """ Return the firmware version. """
        # Overwrite firmware version if fixed to reduce ble reads
        if self._firmware_version is not None:
            return self._firmware_version
        else:
            return self._fetch_device_info()[MI_FIRMWARE]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._fetch_name()

    @property
    def measurement(self):
        """Return measurement dict"""
        return self._fetch_measurement()

    @property
    def temperature(self):
        """Return temperature measurement"""
        return self._fetch_measurement()[MI_TEMPERATURE]

    @property
    def light(self):
        """Return brightness measurement"""
        return self._fetch_measurement()[MI_LIGHT]

    @property
    def moisture(self):
        """Return moisture measurement"""
        return self._fetch_measurement()[MI_MOISTURE]

    @property
    def conductivity(self):
        """Return conductivity measurement"""
        return self._fetch_measurement()[MI_CONDUCTIVITY]

    @auto_connect
    def _fetch_device_info(self):
        """Fetch device battery and firmware info"""
        response = self.read(handle_device_info)
        return self._decode_device_info(response)

    @auto_connect
    def _fetch_device_time(self):
        """Fetch device time"""
        start = time.time()
        response = self.read(handle_device_time)
        ts = (time.time() + start) / 2

        return {
            MI_DEVICE_TIME: int.from_bytes(response, BYTEORDER),
            MI_WALL_TIME: ts
        }

    @auto_connect
    def _fetch_name(self):
        """Fetch the name of the sensor."""
        response = self.read(handle_device_name)
        return response.decode('ascii')

    @auto_connect
    def _fetch_measurement(self):
        """Fetch the measurements from the sensor."""
        if self.firmware_version >= "2.6.6":
            self.write(handle_measurement_control, cmd_measurement_read_init, withResponse=True)
        response = self.read(handle_measurement_read)
        if response == INVALID_DATA:
            raise ValueError('Received invalid data from the sensor')
        timestamps = self._fetch_device_time()
        return {**timestamps, **self._decode_measurement(response)}

    @auto_connect
    def _fetch_history(self):
        """Fetch the historical measurements from the sensor. Only tested on firmware 2.9.2"""
        self.write(handle_history_control, cmd_history_read_init, withResponse=True)
        history_info = self.read(handle_history_read)

        history_length = int.from_bytes(history_info[0:2], BYTEORDER)
        if history_length > 0:
            LOGGER.info("Getting %d measurements" % history_length)
            data = []
            for i in range(history_length):
                payload = cmd_history_address(i)
                try:
                    self.write(handle_history_control, payload, withResponse=True)
                    response = self.read(handle_history_read)
                    if response != (0).to_bytes(16, BYTEORDER):  # Not invalid
                        LOGGER.debug("History item retrieved")
                        data.append(self._decode_history(response))
                except BTLEException:
                    LOGGER.debug("History read failed")
                    self.write(handle_history_control, cmd_history_read_failed)

                LOGGER.info("%.0f%%" % (100 * (i + 1) / history_length))
            self.write(handle_history_control, cmd_history_read_success, withResponse=True)

            _time = self._fetch_device_time()
            time_diff = _time[MI_WALL_TIME] - _time[MI_DEVICE_TIME]
            for entry in data:
                entry[MI_WALL_TIME] = datetime.fromtimestamp(entry[MI_DEVICE_TIME] + time_diff)

            return data

    def _decode_device_info(self, byte_array):
        """Perform byte magic when decoding the device info."""
        data = {
            MI_BATTERY: int.from_bytes(byte_array[0:1], BYTEORDER),
            MI_FIRMWARE: byte_array[2:7].decode('ascii')
        }
        LOGGER.debug('Raw data for char 0x38: %s', self._format_bytes(byte_array))
        LOGGER.debug('battery: %d', data[MI_BATTERY])
        LOGGER.debug('version: %s', data[MI_FIRMWARE])
        return data

    def _decode_measurement(self, byte_array):
        """Perform byte magic when decoding measurements."""
        # negative numbers are stored in one's complement
        temp_bytes = byte_array[0:2]
        if temp_bytes[1] & 0x80 > 0:
            temp_bytes = [temp_bytes[0] ^ 0xFF, temp_bytes[1] ^ 0xFF]

        data = {
            MI_TEMPERATURE: int.from_bytes(temp_bytes, BYTEORDER)/10.0,
            MI_LIGHT: int.from_bytes(byte_array[3:5], BYTEORDER),
            MI_MOISTURE: int.from_bytes(byte_array[7:8], BYTEORDER),
            MI_CONDUCTIVITY: int.from_bytes(byte_array[8:10], BYTEORDER)
        }
        LOGGER.debug('Raw data for char 0x35: %s', self._format_bytes(byte_array))
        LOGGER.debug('temp: %f', data[MI_TEMPERATURE])
        LOGGER.debug('brightness: %d', data[MI_LIGHT])
        LOGGER.debug('conductivity: %d', data[MI_CONDUCTIVITY])
        LOGGER.debug('moisture: %d', data[MI_MOISTURE])
        return data

    def _decode_history(self, byte_array):
        """Perform byte magic when decoding history data."""
        # negative numbers are stored in one's complement
        temp_bytes = byte_array[4:6]
        if temp_bytes[1] & 0x80 > 0:
            temp_bytes = [temp_bytes[0] ^ 0xFF, temp_bytes[1] ^ 0xFF]

        data = {
            MI_DEVICE_TIME: int.from_bytes(byte_array[:4], BYTEORDER),
            MI_TEMPERATURE: int.from_bytes(temp_bytes, BYTEORDER)/10.0,
            MI_LIGHT: int.from_bytes(byte_array[7:10], BYTEORDER),
            MI_MOISTURE: byte_array[11],
            MI_CONDUCTIVITY: int.from_bytes(byte_array[12:14], BYTEORDER)
        }
        LOGGER.debug('Raw data for char 0x3c: %s', self._format_bytes(byte_array))
        LOGGER.debug('device time: %d', data[MI_DEVICE_TIME])
        LOGGER.debug('temp: %f', data[MI_TEMPERATURE])
        LOGGER.debug('brightness: %d', data[MI_LIGHT])
        LOGGER.debug('conductivity: %d', data[MI_CONDUCTIVITY])
        LOGGER.debug('moisture: %d', data[MI_MOISTURE])
        return data

    @property
    def connected(self):
        """Check if device is believed to be connected."""
        return True if self._peripheral._helper is not None else False

    def _connect(self):
        """Connect self._peripheral to the device."""
        self._peripheral.connect(self._mac, ADDR_TYPE_PUBLIC, iface=self._iface)

    def reconnect_on_disconnect(self, exception: BTLEException):
        """Callback for reconnecting after an untimely disconnect
        (the device stops the connection after approximately 3 sec)."""
        assert type(exception) is BTLEException
        if exception.code == BTLEException.DISCONNECTED:
            LOGGER.debug("reconnecting after retry")
            self._connect()

    def __enter__(self):
        self._lock.acquire()
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._peripheral.__exit__(exc_type, exc_val, exc_tb)
        self._lock.release()

    @staticmethod
    def _format_bytes(raw_data):
        """Prettyprint a byte array."""
        return ' '.join([format(c, "02x") for c in raw_data])