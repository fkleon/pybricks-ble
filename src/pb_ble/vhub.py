import sys
from contextlib import AsyncExitStack
from typing import Optional, Sequence, Tuple, Union

from dbus_fast.aio import MessageBus, ProxyObject
from dbus_fast.constants import BusType
from pybricks.hubs import _common

from .bluezdbus import (
    BlueZBroadcaster,
    BlueZPybricksObserver,
    PybricksBroadcastAdvertisement,
    get_adapter,
    get_adapter_details,
)


class VirtualBLE(_common.BLE, AsyncExitStack):
    DEFAULT_DEVICE_NAME = "pb_vhub"
    DEFAULT_DEVICE_VERSION = "1.0"

    _adv: PybricksBroadcastAdvertisement

    def __init__(
        self,
        broadcaster: BlueZBroadcaster,
        observer: BlueZPybricksObserver,
        broadcast_channel: int,
        device_name: str = DEFAULT_DEVICE_NAME,
        device_version: str = DEFAULT_DEVICE_VERSION,
    ):
        super(AsyncExitStack, self).__init__()
        self.device_name = device_name
        self.device_version = device_version
        self.broadcaster = broadcaster
        self.observer = observer
        self._adv = PybricksBroadcastAdvertisement(self.device_name, broadcast_channel)

    async def __aenter__(self):
        try:
            await self.enter_async_context(self.broadcaster)
            await self.enter_async_context(self.observer)
        except Exception:
            if not await self.__aexit__(*sys.exc_info()):
                raise
        return self

    async def broadcast(self, data: Union[bool, int, float, str, bytes]) -> None:
        if data is None:
            await self.broadcaster.stop_broadcast(self._adv)
        else:
            if not self.broadcaster.is_broadcasting(self._adv):
                await self.broadcaster.broadcast(self._adv)
            self._adv.message = data

    def observe(
        self, channel: int
    ) -> Optional[Tuple[Union[bool, int, float, str, bytes], ...]]:
        advertisement = self.observer.observe(channel)
        return advertisement.data if advertisement is not None else None

    def signal_strength(self, channel: int) -> int:
        advertisement = self.observer.observe(channel)
        return advertisement.rssi if advertisement is not None else -128

    def version(self) -> str:
        return self.device_version


async def get_virtual_ble(
    broadcast_channel: int, observe_channels: Sequence[int] | None = None
) -> _common.BLE:
    bus: MessageBus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    name, details = await get_adapter_details()
    adapter: ProxyObject = await get_adapter(bus, name)

    broadcaster = BlueZBroadcaster(bus, adapter, VirtualBLE.DEFAULT_DEVICE_NAME)
    observer = BlueZPybricksObserver(channels=observe_channels)

    return VirtualBLE(
        broadcaster,
        observer,
        broadcast_channel,
        device_version=str(details["hw_version"]),
    )
