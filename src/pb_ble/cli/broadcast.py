"""
CLI interface to send Pybricks BLE broadcasts.
"""
import argparse
import asyncio
import json
import logging

from pb_ble.advertise import run

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
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "data",
    nargs="+",
    type=json.loads,
    help="Data to broadcast: channel followed by JSON values",
)

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

    asyncio.run(
        run(device_name=args.name, timeout=args.timeout, broadcasts=[tuple(args.data)])
    )


if __name__ == "__main__":
    main()
