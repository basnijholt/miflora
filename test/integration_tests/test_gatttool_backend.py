import unittest
import pytest

from miflora.backends.gatttool import GatttoolBackend

TEST_READ_HANDLE = '0x038'
TEST_WRITE_HANDLE = "0x33"
TEST_WRITE_DATA = "A01F"


class TestGatttoolBackend(unittest.TestCase):

    def setUp(self):
        self.backend = GatttoolBackend(retries=0, timeout=5)

    @pytest.mark.usefixtures("mac")
    def test_read(self):
        self.backend.connect(self.mac)
        result = self.backend.read_handle(TEST_READ_HANDLE)
        self.assertIsNotNone(result)
        self.backend.disconnect()

    @pytest.mark.usefixtures("mac")
    def test_write(self):
        self.backend.connect(self.mac)
        result = self.backend.write_handle(TEST_WRITE_HANDLE, TEST_WRITE_DATA)
        self.assertIsNotNone(result)
        self.backend.disconnect()

    def test_read_not_connected(self):
        try:
            self.backend.read_handle(TEST_READ_HANDLE)
            self.fail('should have thrown an exception')
        except ValueError:
            pass

    def test_check_backend(self):
        self.backend.check_backend()
