"""Run the same tests as in TestGatttoolBackend.

Just use a different backend.
"""
from test.integration_tests.test_gatttool_backend import TestGatttoolBackend
from miflora.backends.bluepy import BluepyBackend


class TestBluepyBackend(TestGatttoolBackend):
    """Run the same tests as in TestGatttoolBackend.

    Just use a different backend.
    """

    def setUp(self):
        """Set up the test environment."""
        self.backend = BluepyBackend()

    def test_scan(self):
        """Test scanning for devices.

        Note: fore the test to pass, there must be at least one BTLE device
        near by.
        """
        devices = BluepyBackend.scan_for_devices(5)
        self.assertGreater(len(devices), 0)
        for device in devices:
            self.assertIsNotNone(device)
