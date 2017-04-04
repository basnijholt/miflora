##############################################
#
# This is open source software licensed under the Apache License 2.0
# http://www.apache.org/licenses/LICENSE-2.0
#
##############################################

import binascii
import logging
import sys
import unittest

from miflora.miflora_poller import MiFloraPoller, \
    MI_TEMPERATURE, MI_LIGHT, MI_CONDUCTIVITY, MI_MOISTURE, \
    MI_BATTERY, MI_FIRMWARE, BYTEORDER
from miflora.decorators import retry
from miflora.tests.mock_peripheral import MockPeripheral

if sys.version_info < (3, 0):
    import mock
else:
    import unittest.mock as mock


# setup logging
logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestMiSensor(unittest.TestCase):

    def setUp(self):
        self.failcount = 0

    @retry(3, Exception)
    def _fail_for_n(self, n):
        self.failcount += 1
        if self.failcount < n:
            raise Exception('Failed %d times' % self.failcount)
        return self.failcount

    def test_retry3(self):
        assert self._fail_for_n(3) == 3

    def test_retry4(self):
        self.assertRaises(Exception, self._fail_for_n(4))

    @mock.patch('miflora.miflora_poller.Peripheral', new=MockPeripheral)
    def test_autoconnect(self):
        s = MiFloraPoller('11:22:33')
        assert s.battery_level == 98
        assert s.connected is False
        with s:
            assert s.battery_level == 98
            assert s.connected is True
        assert s.connected is False

    @mock.patch('miflora.miflora_poller.Peripheral', new=MockPeripheral)
    def test_measure(self):
        s = MiFloraPoller('11:22:33')
        with s:
            assert s.battery_level == 98
            assert s.firmware_version == '2.8.6'
            assert s.light == 53
            assert s.temperature == 20.6
            assert s.conductivity == 200
            assert s.moisture == 28

        # Check loads and connection status
        assert [x[0] for x in s._peripheral._read_log] == [0x38, 0x35, 0x41]
        assert s._peripheral._connected is False

    @mock.patch('miflora.miflora_poller.Peripheral', new=MockPeripheral)
    def test_history(self):
        s = MiFloraPoller('11:22:33')

        assert s._peripheral.history_items == 10
        with s:
            data = s._fetch_history()
        assert s._peripheral.history_items == 0
        assert len(s._peripheral._read_log) == 12
        assert s._fetch_history() is None

    def test_format_bytes(self):
        self.assertEquals('ff 00 1b', MiFloraPoller._format_bytes(bytes([0xff, 0x00, 0x1b])))

    def test_int2bytes(self):
        assert (767).to_bytes(2, BYTEORDER) == b'\xff\x02'

    @mock.patch('miflora.miflora_poller.Peripheral', new=MockPeripheral)
    def test_decode_device_info(self):
        test_data = _str2bytearray("62 1d 32 2e 38 2e 36")
        s = MiFloraPoller('11:22:33')
        data = s._decode_device_info(test_data)
        assert data[MI_BATTERY] == 98
        assert data[MI_FIRMWARE] == '2.8.6'


    @mock.patch('miflora.miflora_poller.Peripheral', new=MockPeripheral)
    def test_decode_measurement(self):
        test_data = _str2bytearray("ce 00 00 35 00 00 00 1c c8 00 02 3c 00 fb 34 9b")
        s = MiFloraPoller('11:22:33')
        data = s._decode_measurement(test_data)
        assert data[MI_TEMPERATURE] == 20.6
        assert data[MI_MOISTURE] == 28
        assert data[MI_CONDUCTIVITY] == 200
        assert data[MI_LIGHT] == 53


def _str2bytearray(hex_string):
    return binascii.unhexlify(hex_string.replace(' ', ''))


