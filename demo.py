#!/usr/bin/env python3

import argparse
from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY


parser = argparse.ArgumentParser()
parser.add_argument('mac')
args = parser.parse_args()

poller = MiFloraPoller(args.mac)
print("Getting data from Mi Flora")
print("FW: {}".format(poller.firmware_version()))
print("Name: {}".format(poller.name()))
print("Temperature: {}".format(poller.parameter_value(MI_TEMPERATURE)))
print("Moisture: {}".format(poller.parameter_value(MI_MOISTURE)))
print("Light: {}".format(poller.parameter_value(MI_LIGHT)))
print("Conductivity: {}".format(poller.parameter_value(MI_CONDUCTIVITY)))
print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))

