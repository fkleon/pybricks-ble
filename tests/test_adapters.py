import pytest
from dbus_fast.aio import ProxyObject

from pb_ble.bluezdbus import get_adapter


async def test_get_default_adapter(message_bus, adapter_name):
    if adapter_name != "hci0":
        pytest.skip(reason=f"Bluetooth adapter name '{adapter_name}' is not default")

    adapter: ProxyObject = await get_adapter(message_bus)
    assert adapter.bus_name == "org.bluez"
    assert adapter.path == "/org/bluez/hci0"


async def test_get_adapter_by_name(message_bus, adapter_name):
    adapter: ProxyObject = await get_adapter(message_bus, adapter_name)
    assert adapter.bus_name == "org.bluez"
    assert adapter.path == f"/org/bluez/{adapter_name}"


async def test_get_adapter_unavailable(message_bus):
    with pytest.raises(ValueError):
        await get_adapter(message_bus, "non-existent")
