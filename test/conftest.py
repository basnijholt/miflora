"""Configure pytest for integration tests."""
import pytest


def pytest_addoption(parser):
    """Add command line parameter '--mac=<some mac>' to pytest."""
    parser.addoption("--mac", action="store", help="mac address of sensor to be used for testing")


@pytest.fixture(scope="class")
def mac(request):
    """Get command line parameter and store it in class"""
    request.cls.mac = request.config.getoption("--mac")