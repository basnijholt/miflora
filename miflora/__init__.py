import sys

if sys.version_info <= (3, 4):
    raise ValueError('this library requires at least Python 3.4. ' +
                     'You\'re running version {}.{} from {}.'.format(
                        sys.version_info.major,
                        sys.version_info.minor,
                        sys.executable))
