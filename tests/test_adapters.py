import pytest
from dbus_fast.aio import MessageBus, ProxyObject

from pb_ble.bluezdbus import get_adapter


async def test_get_default_adapter(message_bus: MessageBus, adapter_name: str) -> None:
    if adapter_name != "hci0":
        pytest.skip(reason=f"Bluetooth adapter name '{adapter_name}' is not default")

    adapter: ProxyObject = await get_adapter(message_bus)
    assert adapter.bus_name == "org.bluez"
    assert adapter.path == "/org/bluez/hci0"


async def test_get_adapter_by_name(message_bus: MessageBus, adapter_name: str) -> None:
    adapter: ProxyObject = await get_adapter(message_bus, adapter_name)
    assert adapter.bus_name == "org.bluez"
    assert adapter.path == f"/org/bluez/{adapter_name}"


async def test_get_adapter_unavailable(message_bus: MessageBus) -> None:
    with pytest.raises(ValueError):
        await get_adapter(message_bus, "non-existent")
