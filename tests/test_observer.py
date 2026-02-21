from typing import AsyncGenerator

import pytest
import pytest_asyncio
from bluetooth_adapters import AdapterDetails
from dbus_fast.aio import MessageBus, ProxyObject

from pb_ble.bluezdbus import (
    BlueZPybricksObserver,
)


def get_adapter1(adapter):
    return adapter.get_interface("org.bluez.Adapter1")


class TestPassiveBlueZObserver:
    @pytest_asyncio.fixture(autouse=True)
    async def require_passive_scan(
        sef, adapter_details: AdapterDetails, adapter_name: str
    ) -> None:
        if not adapter_details["passive_scan"]:
            pytest.skip(
                reason=f"Bluetooth adapter '{adapter_name}' does not support BLE passive scanning"
            )

    @pytest_asyncio.fixture()
    async def observer(self) -> AsyncGenerator[BlueZPybricksObserver, None]:
        async with BlueZPybricksObserver(scanning_mode="passive") as observer:
            yield observer

    def test_create_observer(self, message_bus: MessageBus) -> None:
        observer = BlueZPybricksObserver(
            scanning_mode="passive",
            channels=[0],
            rssi_threshold=-100,
            device_pattern="Pybricks",
        )
        assert observer is not None
        assert observer.channels == [0]
        assert observer.rssi_threshold == -100
        assert observer.device_pattern == "Pybricks"

    async def test_observe(
        self, adapter: ProxyObject, observer: BlueZPybricksObserver
    ) -> None:
        # WHEN a channel is observed
        data = observer.observe(0)

        # THEN there should be no data
        assert data is None

        # AND the bluetooth adapter should not be discovering (passive scan)
        discovering = await get_adapter1(adapter).get_discovering()
        assert discovering is False


class TestActiveBlueZObserver:
    @pytest_asyncio.fixture()
    async def observer(self) -> AsyncGenerator[BlueZPybricksObserver, None]:
        async with BlueZPybricksObserver(scanning_mode="active") as observer:
            yield observer

    async def test_create_observer(
        self, message_bus: MessageBus, adapter: ProxyObject
    ) -> None:
        observer = BlueZPybricksObserver(
            scanning_mode="active",
            channels=[0],
            device_pattern="Name",
        )
        assert observer is not None
        assert observer.channels == [0]
        assert observer.rssi_threshold is None
        assert observer.device_pattern == "Name"

    async def test_observe(
        self, adapter: ProxyObject, observer: BlueZPybricksObserver
    ) -> None:
        # WHEN a channel is observed
        data = observer.observe(0)

        # THEN there should be no data
        assert data is None

        # AND the bluetooth adapter should be discovering (active scan)
        discovering = await get_adapter1(adapter).get_discovering()
        assert discovering is True
