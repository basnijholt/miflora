"""Helper functions for unit tests."""

from struct import unpack
from test import HANDLE_READ_NAME, HANDLE_READ_SENSOR_DATA, HANDLE_READ_VERSION_BATTERY, HANDLE_DEVICE_TIME, \
    HANDLE_HISTORY_READ, HANDLE_HISTORY_CONTROL

from miflora.backends import AbstractBackend


class MockBackend(AbstractBackend):
    """Mockup of a Backend and Sensor.

    The behaviour of this Sensors is based on the knowledge there
    is so far on the behaviour of the sensor. So if our knowledge
    is wrong, so is the behaviour of this sensor! Thus is always
    makes sensor to also test against a real sensor.
    """

    def __init__(self, adapter='hci0'):
        super(MockBackend, self).__init__(adapter)
        self._version = (0, 0, 0)
        self.name = ''
        self.battery_level = 0
        self.temperature = 0.0
        self.brightness = 0
        self.moisture = 0
        self.conductivity = 0
        self.written_handles = []
        self.expected_write_handles = set()
        self.override_read_handles = dict()
        self.is_available = True
        self.handle_0x35_raw = None
        self.history_info = None
        self.history_data = None
        self.local_time = None
        self._history_control = None

    def check_backend(self):
        """This backend is available when the field is set accordingly."""
        return self.is_available

    def set_version(self, major, minor, patch):
        """Sets the version number to be returned."""
        self._version = (major, minor, patch)

    @property
    def version(self):
        """Get the stored version number as string."""
        return '{}.{}.{}'.format(*self._version)

    def read_handle(self, handle):
        """Read one of the handles that are implemented."""
        if handle in self.override_read_handles:
            return self.override_read_handles[handle]
        elif handle == HANDLE_READ_VERSION_BATTERY:
            return self._read_battery_version()
        elif handle == HANDLE_READ_SENSOR_DATA:
            return self._read_sensor_data()
        elif handle == HANDLE_READ_NAME:
            return self._read_name()
        elif handle == HANDLE_HISTORY_READ:
            return self._read_history()
        elif handle == HANDLE_DEVICE_TIME:
            return self.local_time
        else:
            raise ValueError('handle not implemented in mockup')

    def write_handle(self, handle, value):
        """Writing handles just stores the results in a list."""
        if handle == HANDLE_HISTORY_CONTROL:
            self._history_control = value
        else:
            self.written_handles.append((handle, value))
        return handle in self.expected_write_handles

    def _read_battery_version(self):
        """Recreate the battery level and version string from the fields of this class."""
        result = [self.battery_level, 0xFF]
        result += [ord(c) for c in self.version]
        return bytes(result)

    def _read_sensor_data(self):
        """Recreate sensor data from the fields of this class."""
        if self.handle_0x35_raw is not None:
            return self.handle_0x35_raw
        result = [0xFE]*16
        temp = int(self.temperature * 10)
        result[0] = int(temp % 256)
        result[1] = int(temp / 256)

        result[3] = int(self.brightness % 256)
        result[4] = int(self.brightness >> 8)

        result[7] = int(self.moisture)

        result[8] = int(self.conductivity % 256)
        result[9] = int(self.conductivity >> 8)
        return bytes(result)

    def _read_name(self):
        """Convert the name into a byte array and return it."""
        return [ord(c) for c in self.name]

    def _read_history(self):
        """Read the history data with the index set in previous HISTORY_CONTROL operation."""
        if self.history_data is None:
            raise ValueError('history not set')
        (cmd, index,) = unpack('<Bh', self._history_control)
        if cmd == 0xA0:
            return self.history_info
        elif cmd == 0xA1:
            return self.history_data[index]
        else:
            raise ValueError('Unknown command %s', cmd)