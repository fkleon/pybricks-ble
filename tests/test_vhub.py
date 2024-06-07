from asyncio import Barrier, Lock, Semaphore

import pytest
import pytest_asyncio
from bluetooth_adapters import get_dbus_managed_objects

from pb_ble import get_virtual_ble


class TestVirtualBLE:
    async def test_create_vble(self, adapter):
        observer = await get_virtual_ble(broadcast_channel=1, observe_channels=[2])
        assert observer is not None
