"""Library to read data from Mi Flora sensor"""
import sys

assert sys.version_info >= (3, 6), "Miflora requires at least Python 3.6"
from ._version import __version__  # noqa: E402, pylint: disable=wrong-import-position

__all__ = ["__version__"]
