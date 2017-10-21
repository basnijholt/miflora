from miflora.backends import AbstractBackend, BluetoothBackendException


class BluepyBackend(AbstractBackend):

    def __init__(self, adapter='hci0'):
        super(self.__class__, self).__init__(adapter)
        self._peripheral = None

    def connect(self, mac):
        from bluepy.btle import Peripheral

        self._peripheral = Peripheral(mac)

    def disconnect(self):
        self._peripheral.disconnect()
        self._peripheral = None

    def read_handle(self, handle):
        if self._peripheral is None:
            raise BluetoothBackendException('not connected to backend')
        return self._peripheral.readCharacteristic(handle)

    def write_handle(self, handle, value):
        if self._peripheral is None:
            raise BluetoothBackendException('not connected to backend')
        return self._peripheral.writeCharacteristic(handle, value, True)

    def check_backend(self):
        try:
            import bluepy.btle  # noqa: F401
        except ImportError:
            raise BluetoothBackendException('bluepy not found')
