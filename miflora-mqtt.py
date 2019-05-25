#!/usr/bin/env python3

import sys
import argparse
import re
import time
import paho.mqtt.client as mqtt

from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY
from miflora.backends.gatttool import GatttoolBackend
from miflora.backends.bluepy import BluepyBackend

def valid_miflora_mac(mac, pat=re.compile(r"C4:7C:8D:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
    if not pat.match(mac):
        raise argparse.ArgumentTypeError('The MAC address "{}" seems to be invalid'.format(mac))
    return mac

def mac_to_eui64(mac):
    if valid_miflora_mac(mac):
        eui64 = re.sub(r'[.:-]', '', mac).lower()
        eui64 = eui64[0:6] + 'fffe' + eui64[6:]
        eui64 = hex(int(eui64[0:2], 16) ^ 2)[2:].zfill(2) + eui64[2:]
        return eui64
    return None

parser = argparse.ArgumentParser()
parser.add_argument('macs', type=valid_miflora_mac, nargs="*")
parser.add_argument('-b', '--backend', choices=['gatttool', 'bluepy'], default='gatttool')
parser.add_argument('-d', '--devinfo', action='store_true')
parser.add_argument('-e', '--health', action='store_true')
parser.add_argument('-m', '--measurements', action='store_true')
args = parser.parse_args()

backend = None
if args.backend == 'gatttool':
    backend = GatttoolBackend
elif args.backend == 'bluepy':
    backend = BluepyBackend
else:
    raise Exception('unknown backend: {}'.format(args.backend))

mqtt_client = mqtt.Client("test")
mqtt_client.connect("localhost", 1883)

for mac in args.macs:
    topicDeviceInfo = 'OpenCH/TeMoLiFe/{}/PubDeviceInfo'.format(mac_to_eui64(mac))
    topicHealth = 'OpenCH/TeMoLiFe/{}/PubHealth'.format(mac_to_eui64(mac))
    topicMeasurements = 'OpenCH/TeMoLiFe/{}/PubState'.format(mac_to_eui64(mac))

    poller = MiFloraPoller(mac, backend)

    if args.devinfo == True:
       message = '{{"name":"{}","firmware_version":"{}"}}' \
            .format(
                poller.name(),
                poller.firmware_version())
       mqtt_client.publish(topicDeviceInfo, message)

    if args.health == True:
        message = '{{"measurements":[{{"name":"battery","value":{},"units":"%"}}]}}' \
            .format(
                poller.parameter_value(MI_BATTERY))
        mqtt_client.publish(topicHealth, message)

    if args.measurements == True:
        # For Xiaomi Mi Flower fertility units - see https://blog.tyang.org/2018/09/25/my-journey-to-a-smarter-home-part-2/
        message = '{{"measurements":[{{"name":"temperature","value":{},"units":"℃"}},{{"name":"moisture","value":{},"units":"%"}},{{"name":"light","value":{},"units":"lux"}},{{"name":"fertility","value":{},"units":"us/cm"}}]}}' \
            .format(
                poller.parameter_value(MI_TEMPERATURE),
                poller.parameter_value(MI_MOISTURE),
                poller.parameter_value(MI_LIGHT),
                poller.parameter_value(MI_CONDUCTIVITY))
        mqtt_client.publish(topicMeasurements, message)

mqtt_client.disconnect()