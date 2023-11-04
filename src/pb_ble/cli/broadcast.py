"""
CLI interface to send Pybricks BLE broadcasts.
"""
import argparse
import asyncio
import logging
from importlib import import_module

from ..advertise import run

# Requirements
# - asyncio
# - use BlueZ DBus API
# - manage multiple broadcasts
# - allow timeout/single send
# - allow custom local name
# - allow minimal advertisement

# DBus proxies
# - Adapter
# - AdvertisingManager

# DBus services
# - Advertisement
# - Application? Service? Characteristics?

# "Beacon" / "Broadcaster"
# - Adapter
# - Advertisement
# - AdvertisingManager

parser = argparse.ArgumentParser(
    prog="pb_broadcast",
    description="Send Pybricks BLE broadcasts",
)
# TODO: specify channel and data via CLI
"""
parser.add_argument(
    "channels",
    metavar="N [0 to 255]",
    type=int,
    # choices=range(0, 256),
    nargs="*",
    help="Pybricks channels to broadcast on",
)
"""

# recommended to be 10 bytes or less
parser.add_argument(
    "--name",
    required=False,
    default="pb_vhub",  # TODO: Must be valid DBus path segment
    help="Bluetooth device name",
)
parser.add_argument(
    "--timeout",
    required=False,
    type=int,
    default=10,
    help="Broadcast timeout",
)
parser.add_argument(
    "--debug",
    required=False,
    action="store_true",
    help="Enable debug logging",
)


def main():
    args = parser.parse_args()

    if args.debug:
        logging.getLogger("pb_ble").setLevel(logging.DEBUG)

    asyncio.run(run(device_name=args.name, timeout=args.timeout))


if __name__ == "__main__":
    main()
