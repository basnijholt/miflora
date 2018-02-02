"""Library to read data from Mi Flora sensor"""
import sys

# This check must be run first, so that it fails before loading the other modules.
# Otherwise we do not get a clean error message.
if sys.version_info <= (3, 4):
    raise ValueError('this library requires at least Python 3.4. ' +
                     'You\'re running version {}.{} from {}.'.format(
                         sys.version_info.major,
                         sys.version_info.minor,
                         sys.executable))


from miflora.backends.bluepy import BluepyBackend  # noqa: E402 # pylint: disable=wrong-import-position
from miflora.backends.gatttool import GatttoolBackend  # noqa: E402 # pylint: disable=wrong-import-position
from miflora.backends.pygatt import PygattBackend  # noqa: E402 # pylint: disable=wrong-import-position
from miflora.backends import BluetoothBackendException  # noqa: F401 E402 # pylint: disable=wrong-import-position
_ALL_BACKENDS = [BluepyBackend, GatttoolBackend, PygattBackend]


def available_backends():
    """Returns a list of all available backends."""
    return [b for b in _ALL_BACKENDS if b.check_backend()]
