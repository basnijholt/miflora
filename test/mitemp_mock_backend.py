"""Helper functions for unit tests."""
from miflora.backends import AbstractBackend, BluetoothBackendException


_HANDLE_READ_BATTERY_LEVEL = 0x0018
_HANDLE_READ_FIRMWARE_VERSION = 0x0024
_HANDLE_READ_NAME = 0x03
_HANDLE_READ_WRITE_SENSOR_DATA = 0x0010


class MiTempMockBackend(AbstractBackend):
    """Mockup of a Backend and Sensor.

    The behaviour of this Sensors is based on the knowledge there
    is so far on the behaviour of the sensor. So if our knowledge
    is wrong, so is the behaviour of this sensor! Thus is always
    makes sensor to also test against a real sensor.
    """

    def __init__(self, adapter='hci0'):
        super(MiTempMockBackend, self).__init__(adapter)
        self._version = '00.00.66'
        self.name = 'MJ_HT_V1'
        self.battery_level = 0
        self.temperature = 0.0
        self.humidity = 0.0
        self.written_handles = []
        self.expected_write_handles = set()
        self.override_read_handles = dict()
        self.is_available = True
        self._handle_0x03_raw_set = False
        self._handle_0x03_raw = None
        self._handle_0x0010_raw_set = False
        self._handle_0x0010_raw = None
        self._handle_0x0018_raw_set = False
        self._handle_0x0018_raw = None
        self._handle_0x0024_raw_set = False
        self._handle_0x0024_raw = None

    def check_backend(self):
        """This backend is available when the field is set accordingly."""
        return self.is_available

    def set_version(self, version):
        """Sets the version number to be returned."""
        self._version = version

    @property
    def version(self):
        """Get the stored version number as string."""
        return self._version

    def read_handle(self, handle):
        """Read one of the handles that are implemented."""
        if handle in self.override_read_handles:
            return self.override_read_handles[handle]
        elif handle == _HANDLE_READ_BATTERY_LEVEL:
            return self._read_battery_level()
        elif handle == _HANDLE_READ_FIRMWARE_VERSION:
            return self._read_firmware()
        elif handle == _HANDLE_READ_NAME:
            return self._read_name()
        else:
            raise ValueError('handle not implemented in mockup')

    def write_handle(self, handle, value):
        """Writing handles just stores the results in a list."""
        self.written_handles.append((handle, value))
        return handle in self.expected_write_handles

    def wait_for_notification(self, handle, delegate, timeout):
        """Recreate sensor data from the fields of this class."""
        if self._handle_0x0010_raw_set:
            delegate.handleNotification(handle, self._handle_0x0010_raw)
            return
        result = [ord(c) for c in "T={:.1f} H={:.1f}".format(self.temperature, self.humidity)]
        delegate.handleNotification(handle, bytes(result))

    def _read_battery_level(self):
        """Recreate the battery level from the fields of this class."""
        if self._handle_0x0018_raw_set:
            return self._handle_0x0018_raw
        return chr(self.battery_level)

    def _read_firmware(self):
        """Recreate the firmware from the fields of this class."""
        if self._handle_0x0024_raw_set:
            return self._handle_0x0024_raw
        result = [ord(c) for c in self.version]
        return bytes(result)

    def _read_name(self):
        """Convert the name into a byte array and return it."""
        if self._handle_0x03_raw_set:
            return self._handle_0x03_raw
        return [ord(c) for c in self.name]

    @property
    def handle_0x03_raw(self):
        """Getter for handle_0x03_raw."""
        return self._handle_0x03_raw

    @handle_0x03_raw.setter
    def handle_0x03_raw(self, value):
        """Setter for handle_0x03_raw.

        This needs a separate flag so that we can also use "None" as return value.
        """
        self._handle_0x03_raw_set = True
        self._handle_0x03_raw = value

    @property
    def handle_0x0010_raw(self):
        """Getter for handle_0x10_raw."""
        return self._handle_0x0010_raw

    @handle_0x0010_raw.setter
    def handle_0x0010_raw(self, value):
        """Setter for handle_0x10_raw.

        This needs a separate flag so that we can also use "None" as return value.
        """
        self._handle_0x0010_raw_set = True
        self._handle_0x0010_raw = value

    @property
    def handle_0x0018_raw(self):
        """Getter for handle_0x0018_raw."""
        return self._handle_0x0018_raw

    @handle_0x0018_raw.setter
    def handle_0x0018_raw(self, value):
        """Setter for handle_0x0018_raw.

        This needs a separate flag so that we can also use "None" as return value.
        """
        self._handle_0x0018_raw_set = True
        self._handle_0x0018_raw = value

    @property
    def handle_0x0024_raw(self):
        """Getter for handle_0x0024_raw."""
        return self._handle_0x0024_raw

    @handle_0x0024_raw.setter
    def handle_0x0024_raw(self, value):
        """Setter for handle_0x0024_raw.

        This needs a separate flag so that we can also use "None" as return value.
        """
        self._handle_0x0024_raw_set = True
        self._handle_0x0024_raw = value


class ConnectExceptionBackend(AbstractBackend):
    """This backend always raises Exceptions."""

    def connect(self, mac):
        """Raise exception when connecting."""
        raise BluetoothBackendException('always raising exceptions')

    def disconnect(self):
        """Disconnect always works"""

    def check_backend(self):
        """check backend must pass so that we get to the BT communication."""
        return True


class RWExceptionBackend(AbstractBackend):
    """This backend always raises Exceptions."""

    def connect(self, mac):
        """Connect always works"""

    def disconnect(self):
        """Disconnect always works"""

    def check_backend(self):
        """check backend must pass so that we get to the BT communication."""
        return True

    def read_handle(self, _):
        """Reading always fails."""
        raise BluetoothBackendException('always raising')

    def read_write(self, _, __):  # pylint: disable=no-self-use
        """Writing always fails."""
        raise BluetoothBackendException('always raising')

    def wait_for_notification(self, handle, delegate, timeout):
        raise BluetoothBackendException('always raising')
