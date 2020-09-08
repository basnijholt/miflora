"""Library to read data from Mi Flora sensor"""
import sys

# This check must be run first, so that it fails before loading the other modules.
# Otherwise we do not get a clean error message.
min_python_version = (3, 6)
if sys.version_info < min_python_version:
    raise ValueError(
        "miflora requires Python≥{}.{}. You're running version {}.{} from {}.".format(
            *min_python_version, *sys.version_info[:2], sys.executable
        )
    )
from ._version import __version__  # noqa: E402, pylint: disable=wrong-import-position

__all__ = ["__version__"]
