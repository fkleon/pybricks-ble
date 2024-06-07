"""
This module contains a generic implementation of the BLE "Broadcaster" role.
"""

import asyncio
from contextlib import AbstractAsyncContextManager
from typing import (
    Optional,
    overload,
)

from dbus_fast.aio import MessageBus, ProxyObject
from dbus_fast.errors import DBusError

from .advertisement import (
    BroadcastAdvertisement,
    LEAdvertisingManager,
)


class BlueZBroadcaster(AbstractAsyncContextManager):
    """
    A BLE broadcaster backed by BlueZ.

    Supports multiple advertising sets in parallel.
    """

    def __init__(self, bus: MessageBus, adapter: ProxyObject, name: str):
        self.bus = bus
        self.adapter = adapter
        self.name = name
        self.adv_manager = LEAdvertisingManager(adapter)
        self.path_namespace = f"/org/bluez/{self.name}"
        self.advertisements: dict[str, BroadcastAdvertisement] = {}

    @overload
    async def stop_broadcast(self, adv: BroadcastAdvertisement): ...
    async def stop_broadcast(self, adv: str):
        if isinstance(adv, BroadcastAdvertisement):
            path = adv.path
        else:
            path = adv

        try:
            await self.adv_manager.unregister_advertisement(path)
        except DBusError:
            # Advertisement does not exist
            pass
        finally:
            self.bus.unexport(path)
            del self.advertisements[path]

    async def stop(self):
        await asyncio.gather(
            *[self.stop_broadcast(path) for path in self.advertisements.keys()]
        )

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()

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

    def is_broadcasting(self, adv: Optional[BroadcastAdvertisement]) -> bool:
        if adv is not None:
            return adv.path in self.advertisements
        else:
            return len(self.advertisements) > 0
