# miflora - Library for Xiaomi Mi plant sensor

[![PyPI](https://img.shields.io/pypi/v/miflora.svg)](https://pypi.python.org/pypi/miflora)
[![PyPI](https://img.shields.io/pypi/status/miflora.svg)](https://pypi.python.org/pypi/miflora)
[![PyPI](https://img.shields.io/pypi/format/miflora.svg)](https://pypi.python.org/pypi/miflora)
[![Travis](https://img.shields.io/travis/open-homeautomation/miflora.svg)](https://travis-ci.org/open-homeautomation/miflora)
[![Coveralls github](https://img.shields.io/coveralls/github/open-homeautomation/miflora.svg)](https://coveralls.io/github/open-homeautomation/miflora)
[![Plants healty and growing](https://img.shields.io/badge/plants-healthy%20and%20growing-green.svg)](https://github.com/open-homeautomation/miflora)
[![GitHub license](https://img.shields.io/github/license/open-homeautomation/miflora.svg)](https://github.com/open-homeautomation/miflora/blob/master/LICENSE)

This library lets you read sensor data from a Xiaomi Mi Flora plant sensor.

* Latest release download: https://pypi.python.org/pypi/miflora
* Build status: https://travis-ci.org/open-homeautomation/miflora
* Test coverage: https://coveralls.io/github/open-homeautomation/miflora

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
* bluez tools (via a wrapper around gatttool)
* pygatt library


### bluepy
To use the [bluepy](https://github.com/IanHarvey/bluepy) library you have to install it on your machine, in most cases this can be done via: 
```pip3 install bluepy``` 

Example to use the bluepy backend:
```python
from miflora.miflora_poller import MiFloraPoller
from btlewrap.bluepy import BluepyBackend

poller = MiFloraPoller('some mac address', BluepyBackend)
```
This is the backend library to be used.

### bluez/gatttool wrapper
To use the bluez wrapper, you need to install the bluez tools on your machine. No additional python 
libraries are required. Some distrubutions moved the gatttool binary to a separate package. Make sure you have this 
binaray available on your machine.

Example to use the bluez/gatttool wrapper:
```python
from miflora.miflora_poller import MiFloraPoller
from btlewrap.gatttool import GatttoolBackend

poller = MiFloraPoller('some mac address', GatttoolBackend)
```

This backend should only be used, if your platform is not supported by bluepy. 
Note: gatttool is depracated in many Linux distributions.

### pygatt
If you have a Blue Giga based device that is supported by [pygatt](https://github.com/peplin/pygatt), you have to
install the bluepy library on your machine. In most cases this can be done via: 
```pip3 install pygatt``` 

Example to use the pygatt backend:
```python
from miflora.miflora_poller import MiFloraPoller
from btlewrap.pygatt import PygattBackend

poller = MiFloraPoller('some mac address', PygattBackend)
```
# Dependencies
miflora depends on the [btlewrap](https://github.com/ChristianKuehnel/btlewrap) library. If you install miflora via PIP btlewrap will automatically be installed. If not, you will have to install btlewrap manually:

```pip3 install btlewrap``` 

## Conttributing
please have a look at [CONTRIBUTING.md](CONTRIBUTING.md)

## Projects Depending on `miflora`

The following shows a selected list of projects using this library:

* https://github.com/ThomDietrich/miflora-mqtt-daemon - An MQTT Client/Daemon for Smart Home solution integration
* https://home-assistant.io/components/sensor.miflora/ - Integration in Home Assistant
* https://github.com/zewelor/bt-mqtt-gateway - A BT to MQTT gateway which support MiFlora sensors + other devices
