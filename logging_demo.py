import os
import sys
import pandas as pd
import argparse
import logging
from miflora.miflora_poller import MiFloraPoller

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

parser = argparse.ArgumentParser()
parser.add_argument('mac')
parser.add_argument('data_file', default=None, nargs="?")
args = parser.parse_args()

device = MiFloraPoller(args.mac)

with device:
    # Fetch history data from device
    data = device.history

    # Take a measurement from the device
    # data = [device.measurement]

data = pd.DataFrame(data)
logger.info(data)

# Save as csv
if args.data_file is not None and data.empty is False:
    if os.path.exists(args.data_file):
        with open(args.data_file, 'a') as f:
            data.to_csv(f, header=False, index=False)
    else:
        with open(args.data_file, 'w') as f:
            data.to_csv(f, header=True, index=False)
