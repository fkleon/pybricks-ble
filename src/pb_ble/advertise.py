"""
Using dbus-fast to send bluetooth advertisements via BlueZ/DBus.
"""

import asyncio
import logging
from enum import Enum
from math import pi
from typing import (
    Dict,
    Iterable,
    List,
    Literal,
    NamedTuple,
    Set,
    Tuple,
    Union,
    no_type_check,
)

from bleak.assigned_numbers import AdvertisementDataType
from bleak.backends.bluezdbus import defs
from bluetooth_adapters import get_adapters
from dbus_fast.aio import MessageBus, ProxyInterface, ProxyObject
from dbus_fast.constants import BusType
from dbus_fast.service import PropertyAccess, ServiceInterface, dbus_property, method
from dbus_fast.signature import Variant
from pybricksdev.ble.lwp3 import LEGO_CID

from .bluezdbus import BroadcastAdvertisement, LEAdvertisingManager, get_adapter
from .messages import encode_message, pack_pnp_id

log = logging.getLogger(name=__name__)


async def run(
    timeout: int,
    device_name: str,
    broadcasts: List[Tuple[any]],
):
    # Connect to D-Bus
    bus: MessageBus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    # Get bluetooth adapter
    adapter: ProxyObject = await get_adapter(bus)

    # Get advertising manager
    bluez_advertising_manager = adapter.get_interface(
        LEAdvertisingManager.INTERFACE_NAME
    )

    # pnp_id = pack_pnp_id(product_id=0x00, product_rev=0x00)

    for broadcast in broadcasts:
        channel, *data = broadcast
        message = encode_message(channel, *data)

        advertisement = BroadcastAdvertisement(device_name, channel)
        advertisement._timeout = timeout
        advertisement._manufacturer_data = {LEGO_CID: Variant("ay", message)}
        # advertisement._service_data = {PNP_ID_UUID: Variant("ay", pnp_id)}

        log.info("Broadcasting on channel %i: %s", channel, data)
        bus.export(advertisement.path, advertisement)
        await bluez_advertising_manager.call_register_advertisement(
            advertisement.path, {}
        )

    # TODO await all on_release instead of fixed time
    await asyncio.sleep(timeout + 1)
    log.debug("Stopping..")
