import unittest

from miflora.backends import BluetoothInterface

from test.unit_tests import MockBackend


class TestBluetoothInterface(unittest.TestCase):

    def test_context_manager_locking(self):
        bt = BluetoothInterface(MockBackend)
        self.assertFalse(bt.is_connected())

        with bt.connect('abc') as connection:
            self.assertTrue(bt.is_connected())

        self.assertFalse(bt.is_connected())
