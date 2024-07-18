import pytest
import pytest_asyncio
from dbus_fast.errors import DBusError

from pb_ble.bluezdbus import LEAdvertisement, LEAdvertisingManager
from pb_ble.bluezdbus.advertisement import Include, Type


class TestLEAdvertising:
    @pytest.mark.parametrize(
        "name,index,path",
        [
            ("test", 0, "/org/bluez/test/advertisement000"),
            ("test", 100, "/org/bluez/test/advertisement100"),
            ("test", 1000, "/org/bluez/test/advertisement1000"),
        ],
    )
    def test_advertisement_path(self, name, index, path):
        adv = LEAdvertisement(
            advertising_type=Type.BROADCAST, local_name=name, index=index
        )
        assert adv.path == path

    def test_invalid_index(self):
        with pytest.raises(ValueError):
            LEAdvertisement(
                advertising_type=Type.BROADCAST, local_name="anything", index=-1
            )

    def test_includes(self):
        adv = LEAdvertisement(
            advertising_type=Type.BROADCAST,
            local_name="test",
            includes={Include.TX_POWER, Include.LOCAL_NAME},
        )

        assert set(adv._includes) == {"tx-power", "local-name"}


class TestLEAdvertisingManager:
    @pytest_asyncio.fixture(autouse=True)
    async def require_advertise(self, adapter_details, adapter_name):
        if not adapter_details["advertise"]:
            pytest.skip(
                reason=f"Bluetooth adapter '{adapter_name}' does not support BLE advertising"
            )

    @pytest.fixture
    def adv_manager(self, adapter):
        return LEAdvertisingManager(adapter)

    @pytest_asyncio.fixture
    async def adv(self, adv_manager):
        adv = LEAdvertisement(advertising_type=Type.BROADCAST, local_name="myadv")
        yield adv
        try:
            await adv_manager.unregister_advertisement(adv)
        except DBusError:
            pass

    @pytest.mark.skip_on_bluez_mock(
        "Incorrect introspection details for properties of type list and dict"
    )
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
        # TODO check exception type and message
        with pytest.raises(DBusError):
            await adv_manager.unregister_advertisement("/some/path")
