# miflora - Library for Xiaomi Mi plant sensor

[![PyPI](https://img.shields.io/pypi/v/miflora.svg)](https://pypi.python.org/pypi/miflora)
[![PyPI](https://img.shields.io/pypi/status/miflora.svg)](https://pypi.python.org/pypi/miflora)
[![PyPI](https://img.shields.io/pypi/format/miflora.svg)](https://pypi.python.org/pypi/miflora)
[![GitHub Actions](https://github.com/basnijholt/miflora/workflows/tox/badge.svg)](https://github.com/basnijholt/miflora/actions)
[![Coveralls github](https://img.shields.io/coveralls/github/basnijholt/miflora.svg)](https://coveralls.io/github/basnijholt/miflora)
[![Plants healty and growing](https://img.shields.io/badge/plants-healthy%20and%20growing-green.svg)](https://github.com/basnijholt/miflora)
[![GitHub license](https://img.shields.io/github/license/basnijholt/miflora.svg)](https://github.com/basnijholt/miflora/blob/master/LICENSE)

> This repo used to live under the [open-homeautomation/miflora](https://github.com/open-homeautomation/miflora) namespace and was originally created by [@open-homeautomation](https://github.com/open-homeautomation).

This library lets you read sensor data from a Xiaomi Mi Flora plant sensor.

* Latest release download: https://pypi.python.org/pypi/miflora
* Build status: https://github.com/basnijholt/miflora/actions
* Test coverage: https://coveralls.io/github/basnijholt/miflora

## Functionality
It supports reading the different measurements from the sensor
- temperature
- moisture
- conductivity
- brightness

To use this library you will need a Bluetooth Low Energy dongle attached to your computer. You will also need a
Xiaomi Mi Flora plant sensor.

## Backends
As there is unfortunately no universally working Bluetooth Low Energy library for Python, the project currently
offers support for two Bluetooth implementations:

* bluepy library
* bluez tools (deprecated, via a wrapper around gatttool)
* pygatt library


### bluepy (recommended)
To use the [bluepy](https://github.com/IanHarvey/bluepy) library you have to install it on your machine, in most cases this can be done via:
```pip3 install bluepy```

Example to use the bluepy backend:
```python
from miflora.miflora_poller import MiFloraPoller
from btlewrap.bluepy import BluepyBackend

poller = MiFloraPoller("some mac address", BluepyBackend)
```
This is the backend library to be used.

### bluez/gatttool wrapper (deprecated)
:warning: The bluez team marked gatttool as deprecated. This solution may still work on some Linux distributions, but it is not recommended any more.

To use the bluez wrapper, you need to install the bluez tools on your machine. No additional python
libraries are required. Some distributions moved the gatttool binary to a separate package. Make sure you have this
binary available on your machine.

Example to use the bluez/gatttool wrapper:
```python
from miflora.miflora_poller import MiFloraPoller
from btlewrap.gatttool import GatttoolBackend

poller = MiFloraPoller("some mac address", GatttoolBackend)
```

This backend should only be used, if your platform is not supported by bluepy.

### pygatt
If you have a Blue Giga based device that is supported by [pygatt](https://github.com/peplin/pygatt), you have to
install the bluepy library on your machine. In most cases this can be done via:
```pip3 install pygatt```

Example to use the pygatt backend:
```python
from miflora.miflora_poller import MiFloraPoller
from btlewrap.pygatt import PygattBackend

poller = MiFloraPoller("some mac address", PygattBackend)
```
## Dependencies
miflora depends on the [btlewrap](https://github.com/ChristianKuehnel/btlewrap) library. If you install miflora via PIP btlewrap will automatically be installed. If not, you will have to install btlewrap manually:

```pip3 install btlewrap```

## Troubleshooting

Users frequently have problems with the communication between their Bluetooth dongle and the sensors. Here are the usual things to try.

### Battery empty
While the battery usually lasts about a year indoor, it may also fail for unknown reasons before that. So the first thing to check if the battery is still good: take out the battery, wait 3 secs and put it back in. The light on the sensor should be flashing. If it is not: get a new battery.

### Range
The distance between Bluetooth dongle and sensor should be less than 5 meters. Try moving the sensor and dongle closer together and see if that solves the problem. If range is an issue, there are a few proxies/relays via MQTT available:
* Linux
  * [plantgateway](https://github.com/ChristianKuehnel/plantgateway)
  * [miflora-mqtt-daemon](https://github.com/ThomDietrich/miflora-mqtt-daemon)
* ESP32
  * [flora](https://github.com/sidddy/flora)

### Outside
If you're operating your sensors outside, make sure the sensor is protected against rain. The power of the battery is decreasing blow -10°C. Sou you might not get readings at that temperature. Also make sure that you have a Bluetooth dongle close by.

### Radio interference
The Bluetooth LE communication is not always reliable. There might be outages due to other radio interferences. The standard solution is to try again or poll your sensor more often that you really need it. It's also the hardest issue to analyse and debug.

### Raspberry Pi
If you're using a Raspberry Pi, make sure, that you OS is up to date, including the latest kernel and firmware. There are sometimes useful Bluetooth fixes. Also make sure that you have a good power supply (3 A recommended) as this causes sporadic problems in many places.

## Conttributing
please have a look at [CONTRIBUTING.md](CONTRIBUTING.md)

## Projects Depending on `miflora`

The following shows a selected list of projects using this library:

* https://github.com/ThomDietrich/miflora-mqtt-daemon - An MQTT Client/Daemon for Smart Home solution integration
* https://home-assistant.io/components/sensor.miflora/ - Integration in Home Assistant
* https://github.com/zewelor/bt-mqtt-gateway - A BT to MQTT gateway which support MiFlora sensors + other devices
* https://github.com/ChristianKuehnel/plantgateway - A MQTT Client to relay sensor data
