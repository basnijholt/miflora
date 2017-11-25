"""Backend for Miflora using the bluepy library."""
from miflora.backends import AbstractBackend, BluetoothBackendException


class BluepyBackend(AbstractBackend):
    """Backend for Miflora using the bluepy library."""

    def __init__(self, adapter='hci0'):
        """Create new instance of the backend."""
        super(self.__class__, self).__init__(adapter)
        self._peripheral = None

    def connect(self, mac):
        """Connect to a device."""
        from bluepy.btle import Peripheral

        self._peripheral = Peripheral(mac)

    def disconnect(self):
        """Disconnect from a device."""
        self._peripheral.disconnect()
        self._peripheral = None

    def read_handle(self, handle):
        """Read a handle from the device.

        You must be connected to do this.
        """
        if self._peripheral is None:
            raise BluetoothBackendException('not connected to backend')
        return self._peripheral.readCharacteristic(handle)

    def write_handle(self, handle, value):
        """Write a handle from the device.

        You must be connected to do this.
        """
        if self._peripheral is None:
            raise BluetoothBackendException('not connected to backend')
        return self._peripheral.writeCharacteristic(handle, value, True)

    def check_backend(self):
        """Check if the backend is available."""
        try:
            import bluepy.btle  # noqa: F401
        except ImportError:
            raise BluetoothBackendException('bluepy not found')

    @staticmethod
    def scan_for_devices(timeout):
        """Scan for bluetooth low energy devices.

        Note this must be run as root!"""
        from bluepy.btle import Scanner

        scanner = Scanner()
        result = []
        for device in scanner.scan(timeout):
            print(device.addr, device.getValueText(9))
            result.append((device.addr, device.getValueText(9)))
        return result
