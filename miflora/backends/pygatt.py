"""Bluetooth backend for Blue Giga based bluetooth devices.

This backend uses the pygatt API: https://github.com/peplin/pygatt
"""
from miflora.backends import AbstractBackend, BluetoothBackendException


class PygattBackend(AbstractBackend):
    """Bluetooth backend for Blue Giga based bluetooth devices."""

    def __init__(self, adapter=None):
        """Create a new instance.

        Note: the parameter "adapter" is ignored, pygatt detects the right USB port automagically.
        """
        super(PygattBackend, self).__init__(adapter)
        self.check_backend()

        import pygatt
        self._adapter = pygatt.BGAPIBackend()
        self._adapter.start()
        self._device = None

    def __del__(self):
        if self._adapter is not None:
            self._adapter.stop()

    def connect(self, mac):
        """Connect to a device."""
        self._device = self._adapter.connect(mac)

    def is_connected(self):
        """Check if connected to a device."""
        return self._device is not None

    def disconnect(self):
        """Disconnect from a device."""
        if self.is_connected():
            self._device.disconnect()
            self._device = None

    def read_handle(self, handle):
        """Read a handle from the device."""
        if not self.is_connected():
            raise BluetoothBackendException('Not connected to device!')
        return self._device.char_read_handle(handle)

    def write_handle(self, handle, value):
        """Write a handle to the device."""
        if not self.is_connected():
            raise BluetoothBackendException('Not connected to device!')
        self._device.char_write_handle(handle, value, True)
        return True

    def check_backend(self):
        """Check if the backend is available."""
        try:
            import pygatt
            return True
        except ImportError:
            return False
