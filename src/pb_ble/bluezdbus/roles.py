import asyncio
import logging
import re
from contextlib import AbstractAsyncContextManager
from enum import Enum
from math import pi
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    NamedTuple,
    Optional,
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
from dbus_fast.errors import DBusError, InvalidObjectPathError
from dbus_fast.service import PropertyAccess, ServiceInterface, dbus_property, method
from dbus_fast.signature import Variant

from ..messages import decode_message, encode_message, pack_pnp_id
from .advertisement import (
    BroadcastAdvertisement,
    LEAdvertisement,
    LEAdvertisingManager,
)

log = logging.getLogger(name=__name__)


class PybricksBroadcast(BroadcastAdvertisement):
    """
    Implementation of a Pybricks broadcast advertisement.

    The data to broadcast is set via the message property.
    """

    LEGO_CID = 0x0397
    """LEGO System A/S company identifier."""

    def __init__(
        self,
        local_name: str,
        channel: int = 0,
        on_release: Callable[[str], None] = lambda path: None,
    ):
        super().__init__(local_name, channel, on_release)

    @property
    def channel(self) -> int:
        return self.index

    @property
    def message(self) -> Optional[Tuple[Union[bool, int, float, str, bytes]]]:
        if self.LEGO_CID in self._manufacturer_data:
            channel, value = decode_message(self._manufacturer_data[self.LEGO_CID])
            return value

    @message.setter
    def message(self, value: Tuple[Union[bool, int, float, str, bytes]]):
        message = encode_message(self.channel, *value)
        self._manufacturer_data[self.LEGO_CID] = Variant("ay", message)
        # Notify BlueZ of the changed manufacturer data so the advertisement is updated
        self.emit_properties_changed(
            changed_properties={"ManufacturerData": self._manufacturer_data}
        )


class BlueZBroadcaster(AbstractAsyncContextManager):
    """
    A BLE broadcaster backed by BlueZ.
    """

    def __init__(self, bus: MessageBus, adapter: ProxyObject, name: str):
        self.bus = bus
        self.adapter = adapter
        self.name = name
        self.adv_manager = LEAdvertisingManager(adapter)
        self.path_namespace = f"/org/bluez/{self.name}"
        self.advertisements: dict[str, BroadcastAdvertisement] = {}

    async def stop(self):
        for path in list(self.advertisements):
            try:
                await self.adv_manager.unregister_advertisement(path)
            except DBusError:
                # Advertisement does not exist
                pass
            finally:
                self.bus.unexport(path)
                del self.advertisements[path]

    async def __aexit__(self, exc_type, exc, tb):
        self.stop()

    async def broadcast(self, adv: BroadcastAdvertisement):
        # TODO construct advertisement in here to ensure local_name
        assert adv._local_name == self.name, f"{adv.name} != {self.name}"

        # cleanup on release of advertisement
        on_release = adv.on_release

        def release_advertisement(path):
            try:
                self.bus.unexport(path)
                del self.advertisements[path]
            finally:
                on_release(path)

        adv.on_release = release_advertisement

        # TODO: error handling
        try:
            self.bus.export(adv.path, adv)
        except ValueError:
            # Already exported
            raise

        try:
            await self.adv_manager.register_advertisement(adv)
        except DBusError:
            # org.bluez.Error.InvalidArguments
            # org.bluez.Error.AlreadyExists
            # org.bluez.Error.InvalidLength
            # org.bluez.Error.NotPermitted
            raise

        self.advertisements[adv.path] = adv


class BlueZObserver:
    """
    A BLE observer backed by BlueZ.
    """

    def __init__(self, bus: MessageBus, adv_monitor: ProxyInterface):
        pass
