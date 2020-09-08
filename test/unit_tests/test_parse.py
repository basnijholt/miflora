""" Test parsing of binary data.

Created on Jul 8, 2016

@author: matuschd
"""

import unittest
from datetime import datetime
from test.helper import MockBackend

from miflora.miflora_poller import (
    MI_CONDUCTIVITY,
    MI_LIGHT,
    MI_MOISTURE,
    MI_TEMPERATURE,
    MiFloraPoller,
)


class KNXConversionTest(unittest.TestCase):
    """Test parsing of binary data."""

    # in testing access to protected fields is OK
    # pylint: disable=protected-access

    def test_parsing(self):
        """Does the Mi Flora data parser works correctly?"""
        poller = MiFloraPoller(None, MockBackend)
        data = bytes(
            [
                0x25,
                0x01,
                0x00,
                0xF7,
                0x26,
                0x00,
                0x00,
                0x28,
                0x0E,
                0x01,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )
        poller._cache = data
        poller._last_read = datetime.now()
        self.assertEqual(poller._parse_data()[MI_CONDUCTIVITY], 270)
        self.assertEqual(poller._parse_data()[MI_MOISTURE], 40)
        self.assertEqual(poller._parse_data()[MI_LIGHT], 9975)
        self.assertEqual(poller._parse_data()[MI_TEMPERATURE], 29.3)

        data = bytes(
            [
                0xF2,
                0x00,
                0x00,
                0x79,
                0x00,
                0x00,
                0x00,
                0x10,
                0x65,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x000,
            ]
        )
        poller._cache = data
        poller._last_read = datetime.now()
        self.assertEqual(poller._parse_data()[MI_CONDUCTIVITY], 101)
        self.assertEqual(poller._parse_data()[MI_MOISTURE], 16)
        self.assertEqual(poller._parse_data()[MI_LIGHT], 121)
        self.assertEqual(poller._parse_data()[MI_TEMPERATURE], 24.2)
