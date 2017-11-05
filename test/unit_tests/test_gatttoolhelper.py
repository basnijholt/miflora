import unittest
from unittest import mock
from miflora.backends.gatttool import GatttoolBackend
from test import TEST_MAC


class TestGatttoolHelper(unittest.TestCase):

    def test_byte_to_handle(self):
        self.assertEqual('0x0B', GatttoolBackend.byte_to_handle(0x0B))
        self.assertEqual('0xAF', GatttoolBackend.byte_to_handle(0xAF))
        self.assertEqual('0xAABB', GatttoolBackend.byte_to_handle(0xAABB))

    def test_bytes_to_string(self):
        self.assertEqual('0A0B', GatttoolBackend.bytes_to_string(bytes([0x0A, 0x0B])))
        self.assertEqual('0x0C0D', GatttoolBackend.bytes_to_string(bytes([0x0C, 0x0D]), True))

    @mock.patch('miflora.backends.gatttool.Popen')
    def test_read_handle_ok(self, popen_mock):
        gattoutput = [0x00, 0x11, 0xAA, 0xFF]
        _configure_popenmock(popen_mock, 'Characteristic value/descriptor: 00 11 AA FF')
        be = GatttoolBackend()
        be.connect(TEST_MAC)
        result = be.read_handle(0xFF)
        self.assertEqual(gattoutput, result)

    @mock.patch('miflora.backends.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_read_handle_empty_output(self, time_mock, popen_mock):
        _configure_popenmock(popen_mock, '')
        be = GatttoolBackend()
        be.connect(TEST_MAC)
        result = be.read_handle(0xFF)
        self.assertIsNone(result)

    @mock.patch('miflora.backends.gatttool.Popen')
    def test_read_handle_empty_output(self, popen_mock):
        _configure_popenmock(popen_mock, 'Characteristic value/descriptor read failed: Invalid handle')
        be = GatttoolBackend()
        be.connect(TEST_MAC)
        with self.assertRaises(ValueError):
            be.read_handle(0xFF)


def _configure_popenmock(popen_mock, output_string):
    m = mock.Mock()
    m.communicate.return_value = [
        bytes(output_string, encoding='UTF-8'),
        bytes('random text', encoding='UTF-8')]
    popen_mock.return_value.__enter__.return_value = m
