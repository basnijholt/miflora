"""Test helper functions."""

import unittest
from miflora.backends.gatttool import GatttoolBackend


class TestGatttoolHelper(unittest.TestCase):
    """Test helper functions."""

    def test_byte_to_handle(self):
        """Test conversion of handles."""
        self.assertEqual('0x0B', GatttoolBackend.byte_to_handle(0x0B))
        self.assertEqual('0xAF', GatttoolBackend.byte_to_handle(0xAF))
        self.assertEqual('0xAABB', GatttoolBackend.byte_to_handle(0xAABB))

    def test_bytes_to_string(self):
        """Test conversion of byte arrays."""
        self.assertEqual('0A0B', GatttoolBackend.bytes_to_string(bytes([0x0A, 0x0B])))
        self.assertEqual('0x0C0D', GatttoolBackend.bytes_to_string(bytes([0x0C, 0x0D]), True))
