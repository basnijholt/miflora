"""
Reading from the sensor is handled by the command line tool "gatttool" that
is part of bluez on Linux.
No other operating systems are supported at the moment
"""

from threading import Lock, current_thread
import os
import logging
import re
from subprocess import Popen, PIPE, TimeoutExpired, signal
from miflora.backends import AbstractBackend
import time

LOGGER = logging.getLogger(__name__)
LOCK = Lock()


class GatttoolBackend(AbstractBackend):

    def __init__(self, adapter, retries=3, timeout=20):
        super(GatttoolBackend, self).__init__(adapter)
        self.adapter = adapter
        self.retries = retries
        self.timeout = timeout
        self._mac = None

    def connect(self, mac):
        # connection handling is not required when using gatttool, but we still need the mac
        self._mac = mac
        self._connected = True

    def disconnect(self):
        # connection handling is not required when using gatttool
        self._mac = None
        self._connected = False

    def write_handle(self, handle, value):
        """
        Read from a BLE address

        @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
        @param: handle - BLE characteristics handle in format 0xXX
        @param: value - value to write to the given handle
        @param: timeout - timeout in seconds
        """

        if not self.is_connected():
            raise ValueError('Not connected to any device.')

        attempt = 0
        delay = 10
        LOGGER.debug("Enter write_ble (%s)", current_thread())

        while attempt <= self.retries:
            cmd = "gatttool --device={} --char-write-req -a {} -n {} --adapter={}".format(self._mac,
                                                                                        handle,
                                                                                        value,
                                                                                        self.adapter)
            with LOCK:
                LOGGER.debug("Created lock in thread %s",
                             current_thread())
                LOGGER.debug("Running gatttool with a timeout of %s",
                             self.timeout)

                with Popen(cmd,
                           shell=True,
                           stdout=PIPE,
                           stderr=PIPE,
                           preexec_fn=os.setsid) as process:
                    try:
                        result = process.communicate(timeout=self.timeout)[0]
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
            if "successfully" in result:
                LOGGER.debug(
                    "Exit write_ble with result (%s)", current_thread())
                return True

            attempt += 1
            LOGGER.debug("Waiting for %s seconds before retrying", delay)
            if attempt < self.retries:
                time.sleep(delay)
                delay *= 2

        LOGGER.debug("Exit write_ble, no data (%s)", current_thread())
        return False

    def read_handle(self, handle):
        """
        Read from a BLE address

        @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
        @param: handle - BLE characteristics handle in format 0xXX
        @param: timeout - timeout in seconds
        """

        if not self.is_connected():
            raise ValueError('Not connected to any device.')

        attempt = 0
        delay = 10
        LOGGER.debug("Enter read_ble (%s)", current_thread())

        while attempt <= self.retries:
            cmd = "gatttool --device={} --char-read -a {} --adapter={}".format(self._mac,
                                                                             handle,
                                                                             self.adapter)
            with LOCK:
                LOGGER.debug("Created lock in thread %s",
                             current_thread())
                LOGGER.debug("Running gatttool with a timeout of %s",
                             self.timeout)

                with Popen(cmd,
                           shell=True,
                           stdout=PIPE,
                           stderr=PIPE,
                           preexec_fn=os.setsid) as process:
                    try:
                        result = process.communicate(timeout=self.timeout)[0]
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
            if attempt < self.retries:
                time.sleep(delay)
                delay *= 2

        LOGGER.debug("Exit read_ble, no data (%s)", current_thread())
        return None
