import sys
from miflora.backends.bluepy import BluepyBackend
from miflora.backends.gatttool import GatttoolBackend

if sys.version_info <= (3, 4):
    raise ValueError('this library requires at least Python 3.4. ' +
                     'You\'re running version {}.{} from {}.'.format(
                        sys.version_info.major,
                        sys.version_info.minor,
                        sys.executable))


_ALL_BACKENDS = [BluepyBackend, GatttoolBackend]


def available_backends():
    """Returns a list of all available backends."""
    return [b for b in _ALL_BACKENDS if b.check_backend()]
