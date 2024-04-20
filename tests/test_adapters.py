import pytest
from dbus_fast.aio import ProxyObject

from pb_ble.bluezdbus import get_adapter

pytestmark = pytest.mark.asyncio


async def test_get_default_adapter(message_bus):
    adapter: ProxyObject = await get_adapter(message_bus)
    assert adapter.bus_name == "org.bluez"
    assert adapter.path == "/org/bluez/hci0"


async def test_get_adapter_by_name(message_bus):
    adapter: ProxyObject = await get_adapter(message_bus, "hci0")
    assert adapter.bus_name == "org.bluez"
    assert adapter.path == "/org/bluez/hci0"


async def test_get_adapter_unavailable(message_bus):
    with pytest.raises(ValueError):
        await get_adapter(message_bus, "non-existent")
