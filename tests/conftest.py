import asyncio

import pytest
import pytest_asyncio
from dbus_fast.aio import MessageBus
from dbus_fast.constants import BusType

from pb_ble.bluezdbus import get_adapter, get_adapter_details


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def message_bus():
    bus: MessageBus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    return bus


@pytest_asyncio.fixture(scope="session")
async def adapter(message_bus):
    name, details = await get_adapter_details()

    if not all([details["passive_scan"], details["advertise"]]):
        pytest.skip(reason="Buetooth adapter must support BLE scanning and advertising")

    assert (
        details["passive_scan"] is True
    ), "Bluetooth adapter must support BLE scanning"
    assert (
        details["advertise"] is True
    ), "Bluetooth adapter must support BLE advertising"

    return await get_adapter(message_bus)
