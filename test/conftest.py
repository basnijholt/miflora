import pytest


def pytest_addoption(parser):
    parser.addoption("--mac", action="store", help="mac address of sensor to be used for testing")


@pytest.fixture(scope="class")
def mac(request):
    request.cls.mac = request.config.getoption("--mac")