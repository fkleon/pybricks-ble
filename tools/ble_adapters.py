"""
List available Bluetooth adapters
"""

import asyncio
from pprint import pp

from bluetooth_adapters import get_adapters, get_dbus_managed_objects

adapters = get_adapters()


async def run():
    dbus_objs = await get_dbus_managed_objects()
    pp(dbus_objs)
    await adapters.refresh()
    pp(adapters.adapters)
    pp(adapters._bluez.adapters)  # type: ignore # _bluez is a private member
    pp(adapters._bluez._packed_managed_objects)  # type: ignore # _bluez is a private member


asyncio.run(run())
