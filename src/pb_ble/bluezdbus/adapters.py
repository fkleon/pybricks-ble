from pprint import pp
from typing import Optional, Tuple

from bleak.backends.bluezdbus import defs
from bluetooth_adapters import (
    AdapterDetails,
    get_adapters,
)
from dbus_fast.aio import MessageBus, ProxyObject

adapters = get_adapters()


class AdapterDetailsExt(AdapterDetails):
    """
    Extended adapter details.
    """

    advertise: bool
    "Whether the adapter supports advertising."


async def get_all_adapter_details() -> dict[str, AdapterDetailsExt]:
    await adapters.refresh()
    adapters_ext = {}

    # Lookup additional details about each adapter
    for adapter, details in adapters.adapters.items():
        bluez_details = adapters._bluez.adapter_details[adapter]
        advertise = "org.bluez.LEAdvertisingManager1" in bluez_details
        adapters_ext[adapter] = AdapterDetailsExt(**details, advertise=advertise)

    return adapters_ext


async def get_adapter_details(adapter_name: str) -> Tuple[str, AdapterDetailsExt]:
    adapters = await get_all_adapter_details()
    return adapter_name, adapters[adapter_name]


async def get_adapter(
    bus: MessageBus, adapter_name: str = adapters.default_adapter
) -> ProxyObject:
    name, details = await get_adapter_details(adapter_name)

    print(f"Using Bluetooth adapter '{name}':")
    pp(details)

    # TODO: Check adapter capabilities here
    if not details["passive_scan"]:
        print("WARNING: Bluetooth adapter cannot observe BLE advertisements!")
    if not details["advertise"]:
        print("WARNING: Bluetooth adapter cannot broadcast BLE advertisements!")

    # TODO: Get path from BlueZ
    adapter_path = f"/org/bluez/{name}"
    adapter_node = await bus.introspect(defs.BLUEZ_SERVICE, adapter_path)
    adapter: ProxyObject = bus.get_proxy_object(
        defs.BLUEZ_SERVICE, adapter_path, adapter_node
    )
    return adapter
