"""
CLI interface to listen for Pybricks BLE broadcasts.
"""
import argparse
import asyncio
import logging

from pb_ble.discover import run

parser = argparse.ArgumentParser(
    prog="pb_observe",
    description="Observe Pybricks BLE broadcasts",
)
parser.add_argument(
    "channels",
    metavar="N [0 to 255]",
    type=int,
    # choices=range(0, 256),
    nargs="*",
    help="Pybricks channels to observe",
)
parser.add_argument(
    "--name",
    required=False,
    default="Pybricks Hub",
    help="Bluetooth device name or Bluetooth address for discovery filter",
)
parser.add_argument(
    "--rssi",
    required=False,
    type=int,
    choices=range(-120, 1),
    metavar="[-120 to 0]",
    help="RSSI threshold for discovery filter",
)
parser.add_argument(
    "--mode",
    required=False,
    choices=["active", "passive"],
    default="active",
    help="BLE scanning mode",
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
        run(
            channels=args.channels,
            device_name=args.name,
            scanning_mode=args.mode,
            rssi_threshold=args.rssi,
        )
    )


if __name__ == "__main__":
    main()
