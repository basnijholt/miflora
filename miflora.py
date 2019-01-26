#!/usr/bin/env python3

import sys
import argparse
import re
import time

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
parser.add_argument('-b', '--backend', choices=['gatttool', 'bluepy'], default='gatttool')
parser.add_argument('-d', '--devinfo', action='store_true')
args = parser.parse_args()

backend = None
if args.backend == 'gatttool':
    backend = GatttoolBackend
elif args.backend == 'bluepy':
    backend = BluepyBackend
else:
    raise Exception('unknown backend: {}'.format(args.backend))

poller = MiFloraPoller(args.mac, backend)

if args.devinfo == True:
    print('{{"name":"{}","fw":"{}","battery":{}}}'
        .format(poller.name(),
            poller.firmware_version(),
            poller.parameter_value(MI_BATTERY)))
else:
    # Xiaomi Mi Flower fertility units - see https://blog.tyang.org/2018/09/25/my-journey-to-a-smarter-home-part-2/
    s = '{{"measurements":[{{"name":"temperature","value":{},"units":"℃"}},{{"name":"moisture","value":{},"units":"%"}},{{"name":"light","value":{},"units":"lux"}},{{"name":"fertility","value":{},"units":"us/cm"}}]}}' \
        .format(
            poller.parameter_value(MI_TEMPERATURE),
            poller.parameter_value(MI_MOISTURE),
            poller.parameter_value(MI_LIGHT),
            poller.parameter_value(MI_CONDUCTIVITY))
    print(s)
