import sys
from contextlib import AsyncExitStack
from typing import ClassVar, Optional, Sequence, Tuple, Union

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
from .constants import ScanningMode


class VirtualBLE(_common.BLE, AsyncExitStack):
    DEFAULT_DEVICE_NAME: ClassVar[str] = "pb_vhub"
    """The default device name to use in data broadcasts."""
    DEFAULT_DEVICE_VERSION: ClassVar[str] = "1.0"
    """The default device version to return from `version()`."""

    _adv: PybricksBroadcastAdvertisement
    """The current data broadcast."""

    def __init__(
        self,
        broadcaster: BlueZBroadcaster,
        observer: BlueZPybricksObserver,
        broadcast_channel: int,
        device_version: str = DEFAULT_DEVICE_VERSION,
    ):
        super(AsyncExitStack, self).__init__()

        self._device_version = device_version
        self._broadcaster = broadcaster
        self._observer = observer

        self._adv = PybricksBroadcastAdvertisement(broadcaster.name, broadcast_channel)

    async def __aenter__(self):
        try:
            await self.enter_async_context(self._broadcaster)
            await self.enter_async_context(self._observer)
        except Exception:
            if not await self.__aexit__(*sys.exc_info()):
                raise
        return self

    async def broadcast(self, data: Union[bool, int, float, str, bytes]) -> None:
        if data is None:
            await self._broadcaster.stop_broadcast(self._adv)
        else:
            if not self._broadcaster.is_broadcasting(self._adv):
                await self._broadcaster.broadcast(self._adv)
            self._adv.message = data

    def observe(
        self, channel: int
    ) -> Optional[Tuple[Union[bool, int, float, str, bytes], ...]]:
        advertisement = self._observer.observe(channel)
        return advertisement.data if advertisement is not None else None

    def signal_strength(self, channel: int) -> int:
        advertisement = self._observer.observe(channel)
        return advertisement.rssi if advertisement is not None else -128

    def version(self) -> str:
        return self._device_version


async def get_virtual_ble(
    device_name: str = VirtualBLE.DEFAULT_DEVICE_NAME,
    broadcast_channel: int = 0,
    observe_channels: Sequence[int] | None = None,
    scanning_mode: ScanningMode = "passive",
    device_filter: str | None = None,
) -> VirtualBLE:
    """
    Creates a "virtual" Pybricks BLE radio that can be used to exchange
    messages with other Pybricks Hubs via connectionless Bluetooth messaging.

    The `VirtualBLE` object implements an interface very similar to the [common Pybricks BLE interface](https://github.com/pybricks/pybricks-api/blob/v3.5.0/src/pybricks/_common.py#L1331)
    available on Pybricks Hubs. The crucial difference is that some methods
    must be called asynchronously.

    `get_virtual_ble()` should be used as an asynchronous context manager:

    ```python
    async with await get_virtual_ble(
        broadcast_channel=2
    ) as vble:
        # Broadcast a random number on channel 2
        val = random.randint(0, 3)
        await vble.broadcast(val)
        # Stop after 10 seconds
        await asyncio.sleep(10)
    ```

    :param device_name: The name of the hub. This may be used as local name
        in the BLE advertisement data, defaults to `VirtualBLE.DEFAULT_DEVICE_NAME`.
    :param broadcast_channel: A value from 0 to 255 indicating which channel
        `VirtualBLE.broadcast()` will use, defaults to 0.
    :param observe_channels: A list of channels to listen to when
        `VirtualBLE.observe()` is called, defaults to None (no channels).
    :param scanning_mode: The scanning mode to use for observing brodcasts,
        defaults to `passive`.
        - Passive scanning is the default and recommended mode.
        However it is not supported by all devices.
        - Active scanning is provided as a well-supported fallback.
        It may negatively impact the power consumption of nearby BLE devices.
    :param device_filter: Provides a mechanism to filter observed broadcasts
        based on the custom name of the sending Pybricks Hub, defaults to None (no filter).
        For example, set this to `Pybricks` to receive only broadcasts from Hubs
        that have a name starting with "Pybricks".
    :return: A `VirtualBLE` object which is loosely adhering to the Pybricks Hub
        BLE interface.
    """
    bus: MessageBus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    name, details = await get_adapter_details()
    adapter: ProxyObject = await get_adapter(bus, name)

    broadcaster = BlueZBroadcaster(bus=bus, adapter=adapter, name=device_name)
    observer = BlueZPybricksObserver(
        scanning_mode=scanning_mode,
        channels=observe_channels,
        device_pattern=device_filter,
    )

    return VirtualBLE(
        broadcaster=broadcaster,
        observer=observer,
        broadcast_channel=broadcast_channel,
        device_version=str(details["hw_version"]),
    )
