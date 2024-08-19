"""
This module contains a generic implementation of the BLE "Broadcaster" role.
"""

import asyncio
import logging
from contextlib import AbstractAsyncContextManager
from typing import (
    overload,
)

from dbus_fast.aio import MessageBus, ProxyObject
from dbus_fast.errors import DBusError

from .advertisement import (
    BroadcastAdvertisement,
    LEAdvertisingManager,
)

log = logging.getLogger(name=__name__)


class BlueZBroadcaster(AbstractAsyncContextManager):
    """
    A BLE broadcaster backed by BlueZ.
    Supports multiple advertising sets in parallel.

    The recommended use is as a context manager, which ensures that all
    registered broadcasts are stopped when exiting the context:

    ```python
    bus = ...
    adapter = ...
    device_name = "my-computer"

    async with BlueZBroadcaster(bus, adapter, device_name) as broadcaster:
        # Start broadcasting
        adv = BroadcastAdvertisement(device_name)
        await broadcaster.broadcast(adv)
        # Stop after 10 seconds
        await asyncio.sleep(10)
    ```
    """

    def __init__(self, bus: MessageBus, adapter: ProxyObject, name: str):
        """
        Creates a new broadcaster.

        :param bus: The message bus.
        :param adapter: The Bluetooth adapter.
        :param name: The name of this broadcaster.
        """
        self.bus: MessageBus = bus
        """The message bus used to connect to DBus."""
        self.adapter: ProxyObject = adapter
        """A DBus proxy object for the Bluetooth adapter to use for advertising."""
        self.name: str = name
        """The name of this broadcaster. Will be used as `local_name` in advertisements."""
        self.adv_manager: LEAdvertisingManager = LEAdvertisingManager(adapter)
        """The BlueZ advertising manager client."""
        self.path_namespace: str = f"/org/bluez/{self.name}"
        """Path prefix to use for DBus objects created by this broadcaster."""
        self.advertisements: dict[str, BroadcastAdvertisement] = {}
        """Active advertisements of this broadcaster."""

    @overload
    async def stop_broadcast(self, adv: str): ...
    @overload
    async def stop_broadcast(self, adv: BroadcastAdvertisement): ...
    async def stop_broadcast(self, adv: str | BroadcastAdvertisement):
        """
        Stop broadcasting the given advertisement.

        :param adv: The broadcast to stop. Takes either the D-Bus path of the
            advertisement, or a reference to the object.
        """
        path = adv.path if isinstance(adv, BroadcastAdvertisement) else adv

        try:
            await self.adv_manager.unregister_advertisement(path)
        except DBusError:
            # Advertisement does not exist
            pass
        finally:
            self.bus.unexport(path)
            del self.advertisements[path]

    async def stop(self):
        """
        Stops this broadcaster. Cleans up any active broadcasts.
        """
        await asyncio.gather(
            *[self.stop_broadcast(path) for path in self.advertisements.keys()]
        )

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()

    async def broadcast(self, adv: BroadcastAdvertisement):
        """
        Start broadcasting the given advertisement.

        :param adv: The reference to the advertisement object.
        :raises ValueError: If a D-Bus object already exists on the given path.
        :raises DBusError: If the given advertisement is invalid, or is already
            registered with BlueZ.
        """
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

        log.info("Broadcasting: %s", adv)

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

    def is_broadcasting(self, adv: BroadcastAdvertisement | None = None) -> bool:
        """
        Checks whether this broadcaster is active.

        :param adv: The reference to the advertisement object to check,
            defaults to None (check if any broadcast is active).
        :return: True if the given (or any) broadcast is active.
        """
        if adv is not None:
            return adv.path in self.advertisements
        else:
            return len(self.advertisements) > 0
