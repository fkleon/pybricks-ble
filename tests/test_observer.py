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
    observer = BlueZPybricksObserver()
    yield observer
    await observer.stop()


class TestBlueZObserver:
    def test_create_observer(self, message_bus):
        observer = BlueZPybricksObserver([0])
        assert observer is not None
