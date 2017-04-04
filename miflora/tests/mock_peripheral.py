import binascii
import logging
from bluepy.btle import BTLEException
from miflora.miflora_poller import BYTEORDER
from miflora import miflora_poller as mi

LOGGER = logging.getLogger(__name__)


def _str2bytearray(hex_string):
    return binascii.unhexlify(hex_string.replace(' ', ''))

VALUE_DEVICE_INFO = _str2bytearray("62 1d 32 2e 38 2e 36")
VALUE_MEASUREMENT = _str2bytearray("ce 00 00 35 00 00 00 1c c8 00 02 3c 00 fb 34 9b")
VALUE_NO_DATA = (0).to_bytes(16, BYTEORDER)
VALUE_DEVICE_TIME = (36000).to_bytes(32, BYTEORDER)


class MockPeripheral:
    def __init__(self, history_items=10, **kwargs):
        self.history_items = history_items
        self.cache = {
            0x03: b'Test Flower Care',
            0x35: VALUE_NO_DATA,
            0x38: VALUE_DEVICE_INFO,
            0x41: VALUE_DEVICE_TIME,
            0x3c: VALUE_NO_DATA
        }
        self._read_log = []
        self._connected = False

    @property
    def _helper(self):
        return 1 if self._connected else None

    def readCharacteristic(self, handle):
        if self._connected is False:
            raise BTLEException(BTLEException.INTERNAL_ERROR, "Helper not started (did you call connect()?)")

        response = self.cache.get(handle, b'\x00\x00')

        self._read_log.append((handle, response))
        LOGGER.debug("read(0x{:x}) value: %a".format(handle, [x for x in response]))
        return response

    def writeCharacteristic(self, handle, payload, withResponse=False):
        LOGGER.debug("write(0x{:x}) payload: %a".format(handle, payload))
        if self._connected is False:
            raise BTLEException(BTLEException.INTERNAL_ERROR, "Helper not started (did you call connect()?)")

        if handle == mi.handle_measurement_control and payload[0] == 0xa0:
            self.cache[mi.handle_measurement_read] = VALUE_MEASUREMENT

        if handle == mi.handle_history_control:
            if payload == mi.cmd_history_read_init:
                self.cache[mi.handle_history_read] = (self.history_items).to_bytes(2, BYTEORDER) + \
                                                     (0).to_bytes(14, BYTEORDER)

            elif payload[0] == int.from_bytes(b'\xa1', BYTEORDER):
                address = int.from_bytes(payload[1:3], byteorder=BYTEORDER)
                self.cache[mi.handle_history_read] = \
                    (3600*(self.history_items - address)).to_bytes(4, BYTEORDER) + \
                    int(20.6*10).to_bytes(2, BYTEORDER) + b'\x00' + \
                    (1066).to_bytes(3, BYTEORDER) + b'\x00' + (57).to_bytes(1, BYTEORDER) + \
                    (123).to_bytes(2, BYTEORDER) + b'\x00\x00'

            elif payload == mi.cmd_history_read_success:
                self.cache[mi.handle_history_read] = VALUE_NO_DATA
                self.history_items = 0

            elif payload == mi.cmd_history_read_failed:
                self.cache[mi.handle_history_read] = VALUE_NO_DATA

        return {'resp': 'wr'} if withResponse else None

    def connect(self, *args, **kwargs):
        self._connected = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connected = False
