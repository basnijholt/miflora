"""Configure pytest for integration tests."""
import logging
import pytest


def pytest_addoption(parser):
    """Setup test environment for pytest.

    Changes:
        - Add command line parameter '--mac=<some mac>' to pytest.
        - enable logging to console
    """
    parser.addoption("--mac", action="store", help="mac address of sensor to be used for testing")
    logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="class")
def mac(request):
    """Get command line parameter and store it in class"""
    request.cls.mac = request.config.getoption("--mac")
