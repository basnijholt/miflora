# Build status:
[![Build Status](https://travis-ci.org/open-homeautomation/miflora.svg?branch=master)](https://travis-ci.org/open-homeautomation/miflora)
[![Coverage Status](https://coveralls.io/repos/github/open-homeautomation/miflora/badge.svg?branch=master)](https://coveralls.io/github/open-homeautomation/miflora?branch=master)

# Testing
The project uses [tox](https://tox.readthedocs.io/en/latest/) for automated testing and dependency mangement and 
[pytest](https://docs.pytest.org/en/latest/) as test framework.

## Unit tests
Install tox and run 'tox' on your command line. This will execute all unit tests. Unit tests do **not** depend on a 
bluetooth dongle or a sensor.

These unit tests are run on TravisCI.

## integration tests
These tests depend on the presence of the real Xiaomi Mi sensors and a Bluteooth LE dongle.
To run these tests call 'tox -e integration_tests -- --mac=<mac of your sensor>'. These test are NOT run on
Travis CI, as they require additional hardware.

