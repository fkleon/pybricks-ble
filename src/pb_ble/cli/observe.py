"""
CLI interface to listen for Pybricks BLE broadcasts.
"""

import argparse
import asyncio
import logging
from typing import Literal, Sequence

from pb_ble.bluezdbus import BlueZPybricksObserver

from . import setup_cli_logging

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
parser.add_argument("--adapter", required=False, help="Bluetooth adapter name")
parser.add_argument(
    "--rssi",
    required=False,
    type=int,
    choices=range(-120, 1),
    metavar="[-120 to 0]",
    help="RSSI threshold",
)
parser.add_argument(
    "--pattern", required=False, default="Pybricks", help="Device name pattern filter"
)
parser.add_argument(
    "--mode",
    required=False,
    choices=["active", "passive"],
    default="passive",
    help="BLE scanning mode",
)
parser.add_argument(
    "--debug",
    required=False,
    action="store_true",
    help="Enable debug logging",
)


async def observe(
    adapter_name: str | None,
    scanning_mode: Literal["active", "passive"],
    channels: Sequence[int] | None,
    rssi_threshold: int | None,
    device_pattern: str | None,
):
    """
    Starts observing data. Prints received broadcasts to the console.

    :param adapter_name: The Bluetooth adapter to use.
    :param scanning_mode: The scanning mode to use.
    :param channels: List of channels to listen on.
    :param rssi_threshold: Minimum required signal strength in dBm.
    :param device_pattern: Device name pattern filter.
    """
    stop_event = asyncio.Event()
    async with BlueZPybricksObserver(
        adapter_name=adapter_name,
        scanning_mode=scanning_mode,
        channels=channels,
        rssi_threshold=rssi_threshold,
        device_pattern=device_pattern,
    ):
        await stop_event.wait()


def main():
    setup_cli_logging()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger("pb_ble").setLevel(logging.DEBUG)

    try:
        asyncio.run(
            observe(
                adapter_name=args.adapter,
                scanning_mode=args.mode,
                channels=args.channels,
                rssi_threshold=args.rssi,
                device_pattern=args.pattern,
            )
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
