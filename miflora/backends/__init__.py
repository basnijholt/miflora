from threading import Lock


class BluetoothInterface(object):
    """Wrapper around the bluetooth adapters.

    This class takes care of locking and the context managers.
    """

    def __init__(self, backend, adapter='hci0', **kwargs):
        self.mac = None
        self.adapter = adapter
        self.lock = Lock()
        self.backend = backend(self.adapter, **kwargs)
        self.backend.check_backend()

    def __del__(self):
        if self.lock.locked():
            self.backend.disconnect()

    def connect(self, mac):
        return _BackendConnection(self, mac)

    def is_connected(self):
        return self.lock.locked()


class _BackendConnection(object):
    """Context Manager for a bluetooth connection.

    This creates the context for the connection and manages locking.
    """

    def __init__(self, bt_interface, mac):
        self._bt_interface = bt_interface
        self.mac = mac

    def __enter__(self):
        self._bt_interface.lock.acquire()
        self._bt_interface.backend.connect(self.mac)
        return self._bt_interface.backend

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: find out what the arguments are good for...
        self._bt_interface.backend.disconnect()
        self._bt_interface.lock.release()


class BluetoothBackendException(Exception):
    pass


class AbstractBackend(object):
    """Abstract base class for talking to Bluetooth LE devices.

    This class will be overridden by the different backends used by miflora.
    """

    def __init__(self, adapter):
        self.adapter = adapter

    def connect(self, mac):
        """connect to a device with the given @mac.

        only required by some backends"""
        pass

    def disconnect(self):
        """disconnect from a device.

        Only required by some backends"""
        pass

    def write_handle(self, handle, value):
        """Write a value to a handle.

        You must be connected to a device first."""
        raise NotImplementedError

    def read_handle(self, handle):
        raise NotImplementedError

    def check_backend(self):
        """Check if the backend is available on the current system.

        Does nothing if the backend is available, throws a BluetoothBackendException
        if it's not available.
        """
        raise NotImplementedError

    def scan_for_devices(self, timeout):
        """Scan for additional devices.

        Returns a list of all the mac addresses of Xiaomi Mi Flower sensor that could be found.
        """
        raise NotImplementedError
