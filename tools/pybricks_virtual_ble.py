import asyncio
import random

from async_timer.pacemaker import TimerPacemaker
from pybricks import _common

from pb_ble import get_virtual_ble


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


async def broadcast(vble, interval: float = 10.0):
    """
    Coroutine that broadcasts a new random number
    on the given interval.
    """
    async for _ in TimerPacemaker(delay=interval):
        val = random.randint(0, 3)
        await vble.broadcast(val)
        print(f"Broadcasting: '{val}'")


async def main():
    broadcast_channel = 1
    observe_channel = 0

    tasks = set()

    async with await get_virtual_ble(broadcast_channel, [observe_channel]) as vble:
        observe_task = asyncio.create_task(observe(vble, observe_channel))
        broadcast_task = asyncio.create_task(broadcast(vble))

        tasks.add(observe_task)
        tasks.add(broadcast_task)

        await asyncio.gather(*tasks)


asyncio.run(main())
