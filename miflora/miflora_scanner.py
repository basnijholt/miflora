"""Scan for miflora devices"""

# use only lower case names here
VALID_DEVICE_NAMES = ["flower mate", "flower care"]

DEVICE_PREFIX = "C4:7C:8D:"


def scan(backend, timeout=10):
    """Scan for miflora devices.

    Note: this must be run as root!
    """
    return [
        mac.upper()
        for (mac, name) in backend.scan_for_devices(timeout)
        if (
            (name is not None and name.lower() in VALID_DEVICE_NAMES)
            or mac is not None
            and mac.upper().startswith(DEVICE_PREFIX)
        )
    ]
