import argparse
from miflora.miflora_poller import MiFloraPoller

parser = argparse.ArgumentParser()
parser.add_argument('mac')
args = parser.parse_args()

device = MiFloraPoller(args.mac)

with device:
    print("Getting data from Mi Flora")
    print("FW: {}".format(device.firmware_version))
    print("Name: {}".format(device.name))
    print("Temperature: {}".format(device.temperature))
    print("Moisture: {}".format(device.moisture))
    print("Light: {}".format(device.light))
    print("Conductivity: {}".format(device.conductivity))
    print("Battery: {}".format(device.battery_level))
