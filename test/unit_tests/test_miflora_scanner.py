"""Test the miflora_scanner."""

import unittest
from miflora import miflora_scanner


class TestMifloraScanner(unittest.TestCase):
    """Test the miflora_scanner."""

    def test_scan(self):
        """Test the scan function."""

        class _MockBackend(object):  # pylint: disable=too-few-public-methods
            """Mock of the backend, always returning the same devices."""

            @staticmethod
            def scan_for_devices(_):
                """Mock for the scan function."""
                return [
                    ('00:FF:FF:FF:FF:FF', None),
                    ('01:FF:FF:FF:FF:FF', 'Flower mate'),
                    ('02:FF:FF:FF:FF:FF', 'Flower care'),
                    ('c4:7c:8d:FF:FF:FF', 'random name'),
                ]

        devices = miflora_scanner.scan(_MockBackend, 0)
        self.assertEqual(len(devices), 3)
        self.assertEqual(devices[0], '01:FF:FF:FF:FF:FF')
        self.assertEqual(devices[1], '02:FF:FF:FF:FF:FF')
        self.assertEqual(devices[2], 'C4:7C:8D:FF:FF:FF')
