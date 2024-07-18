import pytest
import pytest_asyncio

from pb_ble.bluezdbus import (
    BlueZPybricksObserver,
)


class TestPassiveBlueZObserver:
    @pytest_asyncio.fixture(autouse=True)
    async def require_passive_scan(sef, adapter_details, adapter_name):
        if not adapter_details["passive_scan"]:
            pytest.skip(
                reason=f"Bluetooth adapter '{adapter_name}' does not support BLE passive scanning"
            )

    @pytest_asyncio.fixture()
    async def observer(self):
        async with BlueZPybricksObserver(scanning_mode="passive") as observer:
            yield observer

    def test_create_observer(self, message_bus):
        observer = BlueZPybricksObserver(
            scanning_mode="passive", channels=[0], rssi_threshold=-100
        )
        assert observer is not None
        assert observer.channels == [0]
        assert observer.rssi_threshold == -100
        assert observer.device_pattern == "Pybricks"

    async def test_observe(self, adapter, observer):
        # WHEN a channel is observed
        data = observer.observe(0)

        # THEN there should be no data
        assert data is None


class TestActiveBlueZObserver:
    @pytest_asyncio.fixture()
    async def observer(self):
        async with BlueZPybricksObserver(scanning_mode="active") as observer:
            yield observer

    async def test_create_observer(self, message_bus, adapter):
        observer = BlueZPybricksObserver(
            scanning_mode="active",
            channels=[0],
            device_pattern="Name",
        )
        assert observer is not None
        assert observer.channels == [0]
        assert observer.rssi_threshold is None
        assert observer.device_pattern == "Name"

    async def test_observe(self, adapter, observer):
        # WHEN a channel is observed
        data = observer.observe(0)

        # THEN there should be no data
        assert data is None
