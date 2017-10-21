# miflora - Library for Xiaomi Mi plant sensor

This library lets you read sensor data from a Xiaomi Mi Flora plant sensor.


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
* bluez tools (via a wrapper around gatttool)
* bluepy library

### bluez/gatttool wrapper
To use the bluez wrapper, you need to install the bluez tools on your machine. No additional python 
libraries are required.

Example to use the bluez/gatttool wrapper:
```python
from miflora.miflora_poller import MiFloraPoller
from miflora.backends.gatttool import GatttoolBackend

poller = MiFloraPoller('some mac address', GatttoolBackend)
```

### bluepy
To use the bluepy library you have to install it on your machine, in most cases this can be done via: 
```pip3 install bluepy``` 

Example to use the bluez/gatttool wrapper:
```python
from miflora.miflora_poller import MiFloraPoller
from miflora.backends.bluepy import BluepyBackend

poller = MiFloraPoller('some mac address', BluepyBackend)
```

## Conttributing
please have a look at [CONTRIBUTING.md](CONTRIBUTING.md)