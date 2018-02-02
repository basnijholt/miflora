"""
Reading from the sensor is handled by the command line tool "gatttool" that
is part of bluez on Linux.
No other operating systems are supported at the moment
"""

from threading import current_thread
import os
import logging
import re
import time
from subprocess import Popen, PIPE, TimeoutExpired, signal, call
from miflora.backends import AbstractBackend, BluetoothBackendException

_LOGGER = logging.getLogger(__name__)


def wrap_exception(func):
    """Wrap all IOErrors to BluetoothBackendException"""

    def _func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IOError as exception:
            raise BluetoothBackendException() from exception
    return _func_wrapper


class GatttoolBackend(AbstractBackend):
    """ Backend using gatttool."""

    def __init__(self, adapter='hci0', retries=3, timeout=20):
        super(GatttoolBackend, self).__init__(adapter)
        self.adapter = adapter
        self.retries = retries
        self.timeout = timeout
        self._mac = None

    def connect(self, mac):
        """Connect to sensor.

        Connection handling is not required when using gatttool, but we still need the mac
        """
        self._mac = mac

    def disconnect(self):
        """Disconnect from sensor.

        Connection handling is not required when using gatttool.
        """
        self._mac = None

    def is_connected(self):
        """Check if we are connected to the backend."""
        return self._mac is not None

    @wrap_exception
    def write_handle(self, handle, value):
        """Read from a BLE address.

        @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
        @param: handle - BLE characteristics handle in format 0xXX
        @param: value - value to write to the given handle
        @param: timeout - timeout in seconds
        """

        if not self.is_connected():
            raise BluetoothBackendException('Not connected to any device.')

        attempt = 0
        delay = 10
        _LOGGER.debug("Enter write_ble (%s)", current_thread())

        while attempt <= self.retries:
            cmd = "gatttool --device={} --char-write-req -a {} -n {} --adapter={}".format(
                self._mac, self.byte_to_handle(handle), self.bytes_to_string(value), self.adapter)
            _LOGGER.debug("Running gatttool with a timeout of %d: %s",
                          self.timeout, cmd)

            with Popen(cmd,
                       shell=True,
                       stdout=PIPE,
                       stderr=PIPE,
                       preexec_fn=os.setsid) as process:
                try:
                    result = process.communicate(timeout=self.timeout)[0]
                    _LOGGER.debug("Finished gatttool")
                except TimeoutExpired:
                    # send signal to the process group
                    os.killpg(process.pid, signal.SIGINT)
                    result = process.communicate()[0]
                    _LOGGER.debug("Killed hanging gatttool")

            result = result.decode("utf-8").strip(' \n\t')
            if "Write Request failed" in result:
                raise BluetoothBackendException('Error writing handls to sensor: {}'.format(result))
            _LOGGER.debug("Got %s from gatttool", result)
            # Parse the output
            if "successfully" in result:
                _LOGGER.debug(
                    "Exit write_ble with result (%s)", current_thread())
                return True

            attempt += 1
            _LOGGER.debug("Waiting for %s seconds before retrying", delay)
            if attempt < self.retries:
                time.sleep(delay)
                delay *= 2

        raise BluetoothBackendException("Exit write_ble, no data ({})".format(current_thread()))

    @wrap_exception
    def read_handle(self, handle):
        """Read from a BLE address.

        @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
        @param: handle - BLE characteristics handle in format 0xXX
        @param: timeout - timeout in seconds
        """

        if not self.is_connected():
            raise BluetoothBackendException('Not connected to any device.')

        attempt = 0
        delay = 10
        _LOGGER.debug("Enter read_ble (%s)", current_thread())

        while attempt <= self.retries:
            cmd = "gatttool --device={} --char-read -a {} --adapter={}".format(
                self._mac, self.byte_to_handle(handle), self.adapter)
            _LOGGER.debug("Running gatttool with a timeout of %d: %s",
                          self.timeout, cmd)
            with Popen(cmd,
                       shell=True,
                       stdout=PIPE,
                       stderr=PIPE,
                       preexec_fn=os.setsid) as process:
                try:
                    result = process.communicate(timeout=self.timeout)[0]
                    _LOGGER.debug("Finished gatttool")
                except TimeoutExpired:
                    # send signal to the process group
                    os.killpg(process.pid, signal.SIGINT)
                    result = process.communicate()[0]
                    _LOGGER.debug("Killed hanging gatttool")

            result = result.decode("utf-8").strip(' \n\t')
            _LOGGER.debug("Got \"%s\" from gatttool", result)
            # Parse the output
            if "read failed" in result:
                raise BluetoothBackendException("Read error from gatttool: {}".format(result))

            res = re.search("( [0-9a-fA-F][0-9a-fA-F])+", result)
            if res:
                _LOGGER.debug(
                    "Exit read_ble with result (%s)", current_thread())
                return bytes([int(x, 16) for x in res.group(0).split()])

            attempt += 1
            _LOGGER.debug("Waiting for %s seconds before retrying", delay)
            if attempt < self.retries:
                time.sleep(delay)
                delay *= 2

        raise BluetoothBackendException("Exit read_ble, no data ({})".format(current_thread()))

    @staticmethod
    def check_backend():
        """Check if gatttool is available on the system."""
        try:
            call('gatttool', stdout=PIPE, stderr=PIPE)
            return True
        except OSError as os_err:
            msg = 'gatttool not found: {}'.format(str(os_err))
            _LOGGER.error(msg)
        return False

    @staticmethod
    def byte_to_handle(in_byte):
        """Convert a byte array to a handle string."""
        return '0x'+'{:02x}'.format(in_byte).upper()

    @staticmethod
    def bytes_to_string(raw_data, prefix=False):
        """Convert a byte array to a hex string."""
        prefix_string = ''
        if prefix:
            prefix_string = '0x'
        suffix = ''.join([format(c, "02x") for c in raw_data])
        return prefix_string + suffix.upper()
