import pytest
import pytest_asyncio

from pb_ble import get_virtual_ble


@pytest_asyncio.fixture(autouse=True)
async def require_ble(adapter_details, adapter_name):
    if not adapter_details["advertise"] or not adapter_details["passive_scan"]:
        pytest.skip(
            reason=f"Bluetooth adapter '{adapter_name}' does not support BLE capabilities"
        )


class TestVirtualBLE:
    async def test_create_vble(self, adapter):
        ble = await get_virtual_ble(broadcast_channel=1, observe_channels=[2])
        assert ble is not None
        assert not ble._broadcaster.is_broadcasting()

    async def test_observe(self):
        ble = await get_virtual_ble(broadcast_channel=1, observe_channels=[2])
        data = ble.observe(2)
        assert data is None
        assert not ble._broadcaster.is_broadcasting()

    async def test_broadcast(self):
        ble = await get_virtual_ble(broadcast_channel=1, observe_channels=[2])
        await ble.broadcast(42)
        assert ble._broadcaster.is_broadcasting()
        assert ble._adv.message == (42,)

    async def test_broadcast_multiple(self):
        ble = await get_virtual_ble(broadcast_channel=1, observe_channels=[2])
        await ble.broadcast(42, 24)
        assert ble._broadcaster.is_broadcasting()
        assert ble._adv.message == (42, 24)

    async def test_broadcast_none(self):
        ble = await get_virtual_ble(broadcast_channel=1, observe_channels=[2])
        await ble.broadcast(None)
        assert not ble._broadcaster.is_broadcasting()

    async def test_broadcast_start_stop(self):
        ble = await get_virtual_ble(broadcast_channel=1, observe_channels=[2])
        await ble.broadcast(42)
        assert ble._broadcaster.is_broadcasting()
        await ble.broadcast(None)
        assert not ble._broadcaster.is_broadcasting()

    async def test_context(self):
        async with await get_virtual_ble(
            broadcast_channel=1, observe_channels=[2]
        ) as ble:
            assert ble.version() is not None
