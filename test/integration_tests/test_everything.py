import unittest
import pytest
from miflora.miflora_poller import (MiFloraPoller, MI_CONDUCTIVITY,
                                    MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY)


class TestEverything(unittest.TestCase):

    @pytest.mark.usefixtures("mac")
    def test_everything(self):
        assert hasattr(self, "mac")
        poller = MiFloraPoller(self.mac)
        self.assertIsNotNone(poller.firmware_version())
        self.assertIsNotNone(poller.name())
        self.assertIsNotNone(poller.parameter_value(MI_TEMPERATURE))
        self.assertIsNotNone(poller.parameter_value(MI_MOISTURE))
        self.assertIsNotNone(poller.parameter_value(MI_LIGHT))
        self.assertIsNotNone(poller.parameter_value(MI_CONDUCTIVITY))
        self.assertIsNotNone(poller.parameter_value(MI_BATTERY))
