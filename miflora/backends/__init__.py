class AbstractBackend(object):
    """Abstract base class for talking to Bluetooth LE devices.

    This class will be overridden by the different backends used by miflora.
    """

    def __init__(self, adapter='hci0'):
        self.mac = None
        self.adapter = adapter
        self._connected = False

    def __del__(self):
        self.disconnect()

    def connect(self, mac):
        """connect to a device with the given @mac.

        only required by some backends"""
        raise NotImplemented

    def disconnect(self):
        """disconnect from a device.

        only required by some backends"""
        raise NotImplemented

    def is_connected(self):
        return self._connected

    def write_handle(self, handle, value):
        """Write a value to a handle.

        You must be connected to a device first."""
        raise NotImplemented

    def read_handle(self, handle):
        raise NotImplemented
