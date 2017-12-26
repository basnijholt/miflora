"""Backend for Miflora using the bluepy library."""
import re
import logging
from miflora.backends import AbstractBackend, BluetoothBackendException

_LOGGER = logging.getLogger(__name__)


class BluepyBackend(AbstractBackend):
    """Backend for Miflora using the bluepy library."""

    def __init__(self, adapter='hci0'):
        """Create new instance of the backend."""
        super(self.__class__, self).__init__(adapter)
        self._peripheral = None

    def connect(self, mac):
        """Connect to a device."""
        from bluepy.btle import Peripheral
        m = re.search(r'hci([\d]+)', self.adapter)
        if m is None:
            raise ValueError('Invalid pattern "{}" for BLuetooth adpater. '
                             'Expetected something like "hci0".'.format(self.adapter))
        iface = int(m.group(1))
        self._peripheral = Peripheral(mac, iface=iface)

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

    @staticmethod
    def check_backend():
        """Check if the backend is available."""
        try:
            import bluepy.btle  # noqa: F401
            return True
        except ImportError as e:
            _LOGGER.error('bluepy not found: %s', str(e))
        return False

    @staticmethod
    def scan_for_devices(timeout):
        """Scan for bluetooth low energy devices.

        Note this must be run as root!"""
        from bluepy.btle import Scanner

        scanner = Scanner()
        result = []
        for device in scanner.scan(timeout):
            result.append((device.addr, device.getValueText(9)))
        return result
