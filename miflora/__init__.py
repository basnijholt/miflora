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
