from typing import Optional, Sequence, Tuple, Union

from bleak.backends.bluezdbus.manager import get_global_bluez_manager
from dbus_fast.aio import MessageBus, ProxyInterface, ProxyObject
from dbus_fast.constants import BusType
from pybricks.hubs import CityHub, _common

from .bluezdbus import (
    BlueZBroadcaster,
    BlueZPybricksObserver,
    PybricksBroadcastAdvertisement,
    get_adapter,
)


class VirtualBLE(_common.BLE):
    DEFAULT_DEVICE_NAME = "pb_vhub"
    _adv: PybricksBroadcastAdvertisement

    def __init__(
        self,
        broadcaster: BlueZBroadcaster,
        observer: BlueZPybricksObserver,
        broadcast_channel,
        device_name: str = DEFAULT_DEVICE_NAME,
    ):
        self.device_name = device_name
        self.broadcaster = broadcaster
        self.observer = observer
        self._adv = PybricksBroadcastAdvertisement(self.device_name, broadcast_channel)

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
        return self.observer.observe(channel)

    def signal_strength(self, channel: int) -> int:
        # TODO
        return 0

    def version(self) -> str:
        # TODO
        return "0.1"


async def get_virtual_ble(
    broadcast_channel: int, observe_channels: Sequence[int]
) -> _common.BLE:
    # Use bleak manager
    # manager = await get_global_bluez_manager()
    # bus = manager._bus
    # adapter_path = manager.get_default_adapter()
    # adapter: ProxyObject = await get_adapter(bus, adapter_path.split("/")[-1])

    # Use DBus
    bus: MessageBus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    adapter: ProxyObject = await get_adapter(bus)

    broadcaster = BlueZBroadcaster(bus, adapter, VirtualBLE.DEFAULT_DEVICE_NAME)
    observer = BlueZPybricksObserver(channels=observe_channels)

    return VirtualBLE(broadcaster, observer, broadcast_channel)
