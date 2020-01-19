#!/usr/bin/env python3
import argparse
import re
import getmac
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY
from btlewrap import BluepyBackend, GatttoolBackend, PygattBackend

MAC_ADDRESS = r'(?i)[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}'

def valid_mac(mac):
    """ Validates MAC address """
    regex_mac_address = re.compile(MAC_ADDRESS)
    if regex_mac_address.match(mac):
        return mac
    raise argparse.ArgumentTypeError('Invalid MAC address {}'.format(mac))

def mac_to_eui64(mac):
    """ Converts MAC address to EUI64 """
    if valid_mac(mac):
        eui64 = re.sub(r'[.:-]', '', mac).lower()
        eui64 = eui64[0:6] + 'fffe' + eui64[6:]
        eui64 = hex(int(eui64[0:2], 16) ^ 2)[2:].zfill(2) + eui64[2:]
        return eui64
    return None

MI_FLORA_MAC = r'(?i)C4:7C:8D:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}'

def valid_miflora_mac(mac):
    """ Validates Miflora MAC address """
    regex = re.compile(MI_FLORA_MAC)
    if regex.match(mac):
        return mac
    raise argparse.ArgumentTypeError('The MAC address "{}" seems to be invalid'.format(mac))

parser = argparse.ArgumentParser()
parser.add_argument('macs', type=valid_miflora_mac, nargs="*")
parser.add_argument('-s', '--server', default='localhost')
parser.add_argument('-p', '--port', default=1883)
parser.add_argument('-b', '--backend', choices=['gatttool', 'bluepy', 'pygatt'], default='gatttool')
parser.add_argument('-d', '--devinfo', action='store_true')
parser.add_argument('-e', '--health', action='store_true')
parser.add_argument('-m', '--measurements', action='store_true')

backend = None

def get_backend(args):
    """ Returns Bluetooth backend """
    if args.backend == 'gatttool':
        backend = GatttoolBackend
    elif args.backend == 'bluepy':
        backend = BluepyBackend
    elif args.backend == 'pygatt':
        backend = PygattBackend
    else:
        raise Exception('unknown backend: {}'.format(args.backend))
    return backend

args = parser.parse_args()
backend = get_backend(args)
self_mac = getmac.get_mac_address()
self_eui64 = mac_to_eui64(valid_mac(self_mac))
mqtt_client_id = "miflora-mqtt-" + self_eui64

for mac in args.macs:
    sensor_eui64 = mac_to_eui64(mac)
    topicDeviceInfo = 'OpenCH/Gw/{}/TeMoLiFe/{}/Evt/DeviceInfo'.format(self_eui64, sensor_eui64)
    topicHealth = 'OpenCH/Gw/{}/TeMoLiFe/{}/Evt/Health'.format(self_eui64, sensor_eui64)
    topicMeasurements = 'OpenCH/Gw/{}/TeMoLiFe/{}/Evt/State'.format(self_eui64, sensor_eui64)

    poller = MiFloraPoller(mac, backend)
    msgs = []

    try:
        if args.devinfo == True:
            payload = '{{"name":"{}","firmware_version":"{}"}}' \
                .format( \
                    poller.name(), \
                    poller.firmware_version())
            msgs.append({'topic': topicMeasurements, 'payload': payload})     

        if args.health == True:
            payload = '{{"measurements":[{{"name":"battery","value":{},"units":"%"}}]}}' \
                .format( \
                    poller.parameter_value(MI_BATTERY))
            msgs.append({'topic': topicMeasurements, 'payload': payload})     

        if args.measurements == True:
            # For Xiaomi Mi Flower fertility units - see https://blog.tyang.org/2018/09/25/my-journey-to-a-smarter-home-part-2/
            payload = '{{"measurements":[{{"name":"temperature","value":{},"units":"℃"}},{{"name":"moisture","value":{},"units":"%"}},{{"name":"light","value":{},"units":"lux"}},{{"name":"fertility","value":{},"units":"us/cm"}}]}}' \
                .format( \
                    poller.parameter_value(MI_TEMPERATURE), \
                    poller.parameter_value(MI_MOISTURE), \
                    poller.parameter_value(MI_LIGHT), \
                    poller.parameter_value(MI_CONDUCTIVITY))
            msgs.append({'topic': topicMeasurements, 'payload': payload})     
    
    except Exception as e:
        print(mac + ' miflora sensor failure: ' + str(e))

    if len(msgs) > 0:
        publish.multiple(msgs, hostname = args.server, port = args.port, client_id = mqtt_client_id)