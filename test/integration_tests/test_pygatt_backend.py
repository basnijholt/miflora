"""Test the pygatt backend."""
from miflora.backends.pygatt import PygattBackend

from test.integration_tests.test_gatttool_backend import TestGatttoolBackend


class TestPyGattBackend(TestGatttoolBackend):
    """Run the same tests as in TestGatttoolBackend.

    Just use a different backend.
    """

    def setUp(self):
        self.backend = PygattBackend()
