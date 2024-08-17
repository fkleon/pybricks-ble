"""
An example showing a "Virtual Hub BLE radio" operating in Python.
"""

import asyncio
import random

from async_timer.pacemaker import TimerPacemaker
from pybricks import _common

from pb_ble import get_virtual_ble
from pb_ble.constants import ScanningMode


async def observe(vble: _common.BLE, observe_channel: int, interval: float = 1.0):
    """
    Coroutine that polls and prints broadcasting data
    on the given interval.
    """
    async for _ in TimerPacemaker(delay=interval):
        data = vble.observe(observe_channel)
        rssi = vble.signal_strength(observe_channel)
        if data:
            print(f"Observation: '{data}' [{rssi} dBm]")


async def broadcast(vble: _common.BLE, interval: float = 10.0):
    """
    Coroutine that broadcasts a new random number
    on the given interval.
    """
    async for _ in TimerPacemaker(delay=interval):
        val = random.randint(0, 3)
        await vble.broadcast(val)
        print(f"Broadcasting: '{val}'")


async def main():
    # observe config
    scanning_mode: ScanningMode = "passive"
    observe_channel = 0

    # broadcast config
    broadcast_channel = 1

    async with await get_virtual_ble(
        broadcast_channel=broadcast_channel,
        observe_channels=[observe_channel],
        scanning_mode=scanning_mode,
    ) as vble:
        observe_task = asyncio.create_task(observe(vble, observe_channel))
        broadcast_task = asyncio.create_task(broadcast(vble))

        await asyncio.gather(observe_task, broadcast_task)


asyncio.run(main())
