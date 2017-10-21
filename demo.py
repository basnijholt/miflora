#!/usr/bin/env python3

import argparse
import re
import logging

from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY
from miflora.backends.gatttool import GatttoolBackend
from miflora.backends.bluepy import BluepyBackend


def valid_miflora_mac(mac, pat=re.compile(r"C4:7C:8D:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
    if not pat.match(mac):
        raise argparse.ArgumentTypeError('The MAC address "{}" seems to be in the wrong format'.format(mac))
    return mac


parser = argparse.ArgumentParser()
parser.add_argument('mac', type=valid_miflora_mac)
parser.add_argument('--backend', choices=['gatttool', 'bluepy'], default='gatttool')
parser.add_argument('-v', '--verbose', action='store_const', const=True)
args = parser.parse_args()

backend = None
if args.backend == 'gatttool':
    backend = GatttoolBackend
elif args.backend == 'bluepy':
    backend = BluepyBackend
else:
    raise Exception('unknown backend: {}'.format(args.backend))

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

poller = MiFloraPoller(args.mac, backend)

print("Getting data from Mi Flora")
print("FW: {}".format(poller.firmware_version()))
print("Name: {}".format(poller.name()))
print("Temperature: {}".format(poller.parameter_value(MI_TEMPERATURE)))
print("Moisture: {}".format(poller.parameter_value(MI_MOISTURE)))
print("Light: {}".format(poller.parameter_value(MI_LIGHT)))
print("Conductivity: {}".format(poller.parameter_value(MI_CONDUCTIVITY)))
print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))
