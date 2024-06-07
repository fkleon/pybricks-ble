from asyncio import Barrier, Lock, Semaphore

import pytest
import pytest_asyncio
from bluetooth_adapters import get_dbus_managed_objects

from pb_ble.bluezdbus import BlueZBroadcaster, BroadcastAdvertisement

lock = Lock()


@pytest_asyncio.fixture()
async def broadcaster(message_bus, adapter):
    broadcaster = BlueZBroadcaster(bus=message_bus, adapter=adapter, name="vhub")
    await lock.acquire()
    yield broadcaster
    await broadcaster.stop()
    lock.release()


@pytest_asyncio.fixture(autouse=False)
async def broadcast_lock():
    await lock.acquire()
    yield
    lock.release()


class TestBlueZBroadcaster:
    def test_create_broadcaster(self, message_bus, adapter):
        broadcaster = BlueZBroadcaster(bus=message_bus, adapter=adapter, name="vhub")
        assert broadcaster is not None
        assert len(broadcaster.advertisements) == 0

    async def test_stop_broadcaster(self, message_bus, adapter):
        # GIVEN an advertisement on the bus is known to the broadcaster
        broadcaster = BlueZBroadcaster(bus=message_bus, adapter=adapter, name="vhub")
        adv = BroadcastAdvertisement("vhub")
        adv.path = "/some/path"
        message_bus.export(adv.path, adv)
        broadcaster.advertisements = {adv.path: adv}

        # WHEN the broadcaster is stopped
        await broadcaster.stop()

        # THEN the advertisements are removed
        assert len(broadcaster.advertisements) == 0

    async def test_broadcast(self, broadcaster):
        # GIVEN a broadcast
        adv = BroadcastAdvertisement(
            broadcaster.name,
        )

        # WHEN it is sent
        await broadcaster.broadcast(adv)

        # THEN the broadcaster keeps track of the active broadcast
        assert len(broadcaster.advertisements) == 1
        assert adv.path in broadcaster.advertisements

    async def test_broadcast_release(self, broadcaster):
        # GIVEN a broadcast
        semaphore = Semaphore(1)
        adv = BroadcastAdvertisement(
            broadcaster.name,
            on_release=lambda path: semaphore.release(),
        )

        # use semaphore to wait until release
        await semaphore.acquire()

        # use timeout to cause an automatic release by BlueZ
        adv._timeout = 1

        assert adv.path not in broadcaster.advertisements

        # WHEN it is broadcasted and then released
        await broadcaster.broadcast(adv)
        assert adv.path in broadcaster.advertisements

        # wait for release
        assert await semaphore.acquire()

        # THEN it is not in the advertisements list
        assert adv.path not in broadcaster.advertisements

        # TODO: test that it's unexported from the bus

    async def test_broadcast_twice(self, broadcaster):
        # GIVEN a broadcast
        adv = BroadcastAdvertisement(broadcaster.name)

        # WHEN the same broadcast is sent twice
        await broadcaster.broadcast(adv)
        # THEN an error is raised the second time
        with pytest.raises(ValueError):
            await broadcaster.broadcast(adv)
