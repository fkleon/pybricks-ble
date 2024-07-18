import pytest
import pytest_asyncio

from pb_ble.bluezdbus import (
    BlueZPybricksObserver,
)


@pytest_asyncio.fixture(autouse=True)
async def require_passive_scan(adapter_details, adapter_name):
    if not adapter_details["passive_scan"]:
        pytest.skip(
            reason=f"Bluetooth adapter '{adapter_name}' does not support BLE passive scanning"
        )


@pytest_asyncio.fixture()
async def observer():
    async with BlueZPybricksObserver() as observer:
        yield observer


class TestBlueZObserver:
    def test_create_observer(self, message_bus):
        observer = BlueZPybricksObserver([0])
        assert observer is not None

    def test_observe(self, adapter, observer):
        data = observer.observe(0)
        assert data is None
