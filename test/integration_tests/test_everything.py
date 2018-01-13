"""End to End test cases for MiFlora."""
import unittest
import pytest
from miflora.miflora_poller import (MiFloraPoller, MI_CONDUCTIVITY,
                                    MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY)
from miflora.backends.gatttool import GatttoolBackend
from miflora.backends.bluepy import BluepyBackend


class TestEverythingGatt(unittest.TestCase):
    """End to End test cases for MiFlora."""
    # pylint does not understand pytest fixtures, so we have to disable the warning
    # pylint: disable=no-member

    def setUp(self):
        """Setup test environment."""
        self.backend_type = GatttoolBackend

    @pytest.mark.usefixtures("mac")
    def test_everything(self):
        """Test reading data from a sensor

        This check if we can successfully get some data from a real sensor. This test requires bluetooth hardware and a
        real sensor close by.
        """
        assert hasattr(self, "mac")
        poller = MiFloraPoller(self.mac, self.backend_type)
        self.assertIsNotNone(poller.firmware_version())
        self.assertIsNotNone(poller.name())
        self.assertIsNotNone(poller.parameter_value(MI_TEMPERATURE))
        self.assertIsNotNone(poller.parameter_value(MI_MOISTURE))
        self.assertIsNotNone(poller.parameter_value(MI_LIGHT))
        self.assertIsNotNone(poller.parameter_value(MI_CONDUCTIVITY))
        self.assertIsNotNone(poller.parameter_value(MI_BATTERY))


class TestEverythingBluepy(TestEverythingGatt):
    """Run the same tests as in the gatttool test"""

    def setUp(self):
        """Setup test environment."""
        self.backend_type = BluepyBackend
