from asyncio import Barrier, Lock, Semaphore

import pytest
import pytest_asyncio
from bluetooth_adapters import get_dbus_managed_objects
from dbus_fast.errors import DBusError, InvalidObjectPathError

from pb_ble.bluezdbus import LEAdvertisement, LEAdvertisingManager
from pb_ble.bluezdbus.advertisement import Type


@pytest.fixture
def adv_manager(adapter):
    return LEAdvertisingManager(adapter)


@pytest_asyncio.fixture
async def adv(adv_manager):
    adv = LEAdvertisement(advertising_type=Type.BROADCAST, local_name="myadv")
    yield adv
    try:
        await adv_manager.unregister_advertisement(adv)
    except DBusError:
        pass


class TestLEAdvertisingManager:
    async def test_create(self, adapter):
        adv_manager = LEAdvertisingManager(adapter)

        assert isinstance(await adv_manager.active_instances(), int)
        assert isinstance(await adv_manager.supported_instances(), int)
        assert isinstance(await adv_manager.supported_includes(), list)
        assert isinstance(await adv_manager.supported_secondary_channels(), list)
        assert isinstance(await adv_manager.supported_capabilities(), dict)
        assert isinstance(await adv_manager.supported_features(), list)

    async def test_register_advertisement(self, adv_manager, adv):
        await adv_manager.register_advertisement(adv)

    async def test_unregister_advertisement(self, adv_manager, adv):
        await adv_manager.register_advertisement(adv)
        await adv_manager.unregister_advertisement(adv)

    async def test_unregister_advertisement_by_path(self, adv_manager, adv):
        await adv_manager.register_advertisement(adv)
        await adv_manager.unregister_advertisement(adv.path)

    async def test_unregister_advertisement_does_not_exist(self, adv_manager):
        with pytest.raises(DBusError, match="Does Not Exist"):
            await adv_manager.unregister_advertisement("/some/path")
