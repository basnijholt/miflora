#!/usr/bin/env python3

import argparse
import re

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
args = parser.parse_args()

backend = None
if args.backend == 'gatttool':
    backend = GatttoolBackend
elif args.backend == 'bluepy':
    backend = BluepyBackend
else:
    raise Exception('unknown backend: {}'.format(args.backend))

poller = MiFloraPoller(args.mac, backend)

print('{{ "fw": "{0}", "name": "{1}", "temperature": {2}, "moisture": {3}, "light": {4}, "conductivity": {5}, "battery": {6} }}'
    .format(poller.firmware_version(),
            poller.name(),
            poller.parameter_value(MI_TEMPERATURE),
            poller.parameter_value(MI_MOISTURE),
            poller.parameter_value(MI_LIGHT),
            poller.parameter_value(MI_CONDUCTIVITY),
            poller.parameter_value(MI_BATTERY)))
