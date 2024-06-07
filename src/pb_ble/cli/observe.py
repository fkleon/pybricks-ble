"""
CLI interface to listen for Pybricks BLE broadcasts.
"""

import argparse
import asyncio
import logging

from pb_ble.bluezdbus import BlueZPybricksObserver

parser = argparse.ArgumentParser(
    prog="pb_observe",
    description="Observe Pybricks BLE broadcasts",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "channels",
    metavar="N [0 to 255]",
    type=int,
    nargs="*",
    help="Pybricks channels to observe, or all channels if not given.",
)
parser.add_argument(
    "--rssi",
    required=False,
    type=int,
    choices=range(-120, 1),
    metavar="[-120 to 0]",
    help="RSSI threshold",
)
parser.add_argument(
    "--debug",
    required=False,
    action="store_true",
    help="Enable debug logging",
)


async def observe(channels, rssi_threshold):
    stop_event = asyncio.Event()
    async with BlueZPybricksObserver(channels, rssi_threshold):
        await stop_event.wait()


def main():
    args = parser.parse_args()

    if args.debug:
        logging.getLogger("pb_ble").setLevel(logging.DEBUG)

    try:
        asyncio.run(
            observe(
                channels=args.channels,
                rssi_threshold=args.rssi,
            )
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
