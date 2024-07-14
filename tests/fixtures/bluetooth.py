import pytest
from dbus_fast.aio import MessageBus, ProxyObject
from dbus_fast.constants import BusType

from pb_ble.bluezdbus import get_adapter, get_adapter_details


def pytest_addoption(parser):
    parser.addoption(
        "--adapter",
        action="store",
        default="hci0",
        help="Bluetooth adapter device name",
    )


@pytest.fixture
def adapter_name(pytestconfig) -> str:
    return pytestconfig.getoption("adapter")


@pytest.fixture
async def message_bus() -> MessageBus:
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    # await bus.request_name("pb_ble.tests")
    return bus


@pytest.fixture
async def adapter(message_bus: MessageBus, adapter_name: str) -> ProxyObject:
    return await get_adapter(message_bus, adapter_name)


@pytest.fixture
async def adapter_details(adapter_name: str):
    _, details = await get_adapter_details(adapter_name)
    return details
