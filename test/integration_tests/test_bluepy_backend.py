from miflora.backends.bluepy import BluepyBackend

from test.integration_tests.test_gatttool_backend import TestGatttoolBackend


class TestBluepyBackend(TestGatttoolBackend):
    """Run the same tests as in TestGatttoolBackend.

    Just use a different backend.
    """

    def setUp(self):
        self.backend = BluepyBackend()
