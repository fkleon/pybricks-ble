from asyncio import Barrier, Lock, Semaphore

import pytest
import pytest_asyncio
from bluetooth_adapters import get_dbus_managed_objects

from pb_ble.bluezdbus import (
    BlueZBroadcaster,
    BlueZPybricksObserver,
    BroadcastAdvertisement,
)


@pytest_asyncio.fixture()
async def observer():
    async with BlueZPybricksObserver() as observer:
        yield observer


class TestBlueZObserver:
    def test_create_observer(self, message_bus):
        observer = BlueZPybricksObserver([0])
        assert observer is not None

    def test_observe(self, observer):
        data = observer.observe(0)
        assert data is None
