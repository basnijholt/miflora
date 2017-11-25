from miflora.backends.bluepy import BluepyBackend

from test.integration_tests.test_gatttool_backend import TestGatttoolBackend


class TestBluepyBackend(TestGatttoolBackend):
    """Run the same tests as in TestGatttoolBackend.

    Just use a different backend.
    """

    def setUp(self):
        self.backend = BluepyBackend()

    def test_scan(self):
        """Test scanning for devices.

        Note: fore the test to pass, there must be at least one BTLE device
        near by.
        """
        devices = BluepyBackend.scan_for_devices(5)
        self.assertGreater(len(devices), 0)
        for d in devices:
            self.assertIsNotNone(d)
