#!/usr/bin/env python3

import argparse
import re
import logging

from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY
from miflora.backends.bluepy import BluepyBackend
from miflora.backends.gatttool import GatttoolBackend
from miflora import miflora_scanner, available_backends


def valid_miflora_mac(mac, pat=re.compile(r"C4:7C:8D:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
    if not pat.match(mac.upper()):
        raise argparse.ArgumentTypeError('The MAC address "{}" seems to be in the wrong format'.format(mac))
    return mac


def poll(args):
    backend = _get_backend(args)
    poller = MiFloraPoller(args.mac, backend)
    print("Getting data from Mi Flora")
    print("FW: {}".format(poller.firmware_version()))
    print("Name: {}".format(poller.name()))
    print("Temperature: {}".format(poller.parameter_value(MI_TEMPERATURE)))
    print("Moisture: {}".format(poller.parameter_value(MI_MOISTURE)))
    print("Light: {}".format(poller.parameter_value(MI_LIGHT)))
    print("Conductivity: {}".format(poller.parameter_value(MI_CONDUCTIVITY)))
    print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))


def scan(args):
    backend = _get_backend(args)
    print('Scanning for 10 seconds...')
    devices = miflora_scanner.scan(backend, 10)
    print('Found {} devices:'.format(len(devices)))
    for d in devices:
        print('  {}'.format(d))


def _get_backend(args):
    if args.backend == 'gatttool':
        backend = GatttoolBackend
    elif args.backend == 'bluepy':
        backend = BluepyBackend
    else:
        raise Exception('unknown backend: {}'.format(args.backend))
    return backend


def list_backends(args):
    backends = [b.__name__ for b in available_backends()]
    print('\n'.join(backends))


parser = argparse.ArgumentParser()
parser.add_argument('--backend', choices=['gatttool', 'bluepy'], default='gatttool')
parser.add_argument('-v', '--verbose', action='store_const', const=True)
subparsers = parser.add_subparsers(help='sub-command help')

parser_poll = subparsers.add_parser('poll', help='poll data from a sensor')
parser_poll.add_argument('mac', type=valid_miflora_mac)
parser_poll.set_defaults(func=poll)

parser_scan = subparsers.add_parser('scan', help='scan for devices')
parser_scan.set_defaults(func=scan)

parser_scan = subparsers.add_parser('backends', help='list the available backends')
parser_scan.set_defaults(func=list_backends)

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

args.func(args)
