"""Constants unsed in the tests."""

HANDLE_READ_VERSION_BATTERY = 0x38
HANDLE_READ_NAME = 0x03
HANDLE_READ_SENSOR_DATA = 0x35
HANDLE_WRITE_MODE_CHANGE = 0x33

HANDLE_DEVICE_TIME = 0x41
HANDLE_HISTORY_CONTROL = 0x3e
HANDLE_HISTORY_READ = 0x3c

DATA_MODE_CHANGE = bytes([0xA0, 0x1F])

TEST_MAC = '11:22:33:44:55:66'

INVALID_DATA = b'\xaa\xbb\xcc\xdd\xee\xff\x99\x88\x77\x66\x00\x00\x00\x00\x00\x00'
