miflora - Library for Xiaomi Mi plant sensor
============================================

This library lets you read sensor data from a Xiaomi Mi Flora plant sensor.

It supports reading
- temperature
- moisture
- fertility
- light intensity


Testing
=======

*Unit tests:*
Install tox and run 'tox'
These tests are run on TravisCI

*integration tests:*
These tests depend on the presence of the real Xiaomi Mi sensors and a Bluteooth LE dongle.
To run these tests call 'tox -e integration_tests -- --mac=<mac of your sensor>'. These test are NOT run on
Travis CI, as they require additional hardware.


