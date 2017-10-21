import unittest

from miflora.backends.gatttool import GatttoolBackend


class TestGatttoolHelper(unittest.TestCase):

    def test_byte_to_handle(self):
        self.assertEqual('0x0B', GatttoolBackend.byte_to_handle(0x0B))
        self.assertEqual('0xAF', GatttoolBackend.byte_to_handle(0xAF))
        self.assertEqual('0xAABB', GatttoolBackend.byte_to_handle(0xAABB))

    def test_bytes_to_string(self):
        self.assertEqual('0A0B', GatttoolBackend.bytes_to_string(bytes([0x0A, 0x0B])))
        self.assertEqual('0x0C0D', GatttoolBackend.bytes_to_string(bytes([0x0C, 0x0D]), True))
