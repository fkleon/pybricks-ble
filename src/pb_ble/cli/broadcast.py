"""
CLI interface to send Pybricks BLE broadcasts.
"""

import argparse
import asyncio
import json
import logging

from dbus_fast import BusType
from dbus_fast.aio import MessageBus, ProxyObject

from pb_ble import PybricksBroadcastData
from pb_ble.bluezdbus import (
    BlueZBroadcaster,
    PybricksBroadcastAdvertisement,
    get_adapter,
)

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
    help="Bluetooth device name to use for advertisements",
)
parser.add_argument(
    "--timeout",
    required=False,
    type=int,
    default=10,
    help="Broadcast timeout in seconds",
)
parser.add_argument(
    "--debug",
    required=False,
    action="store_true",
    help="Enable debug logging",
)


async def broadcast(
    device_name: str,
    timeout: int,
    channel: int,
    data: PybricksBroadcastData | None,
):
    stop_event = asyncio.Event()

    bus: MessageBus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    adapter: ProxyObject = await get_adapter(bus)

    adv = PybricksBroadcastAdvertisement(
        device_name, channel, data, on_release=lambda p: stop_event.set()
    )
    adv._timeout = timeout

    async with BlueZBroadcaster(bus, adapter, device_name) as broadcaster:
        await broadcaster.broadcast(adv)
        await stop_event.wait()


def main():
    args = parser.parse_args()

    if args.debug:
        logging.getLogger("pb_ble").setLevel(logging.DEBUG)

    channel, *data = args.data

    try:
        asyncio.run(
            broadcast(
                device_name=args.name,
                timeout=args.timeout,
                channel=channel,
                data=tuple(data),
            )
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
