import sys
import unittest.mock

import dbus
import pytest
from dbusmock import SpawnedMock
from dbusmock.testcase import PrivateDBus

from . import YieldFixture


def pytest_runtest_setup(item) -> None:
    skip_on_bluez_mock_marker = item.get_closest_marker("skip_on_bluez_mock")
    if skip_on_bluez_mock_marker is not None:
        reason = skip_on_bluez_mock_marker.args[0] or "Unknown reason"
        raise pytest.skip.Exception(
            f"Skipped on BlueZ Mock: {reason}", _use_item_location=True
        )


@pytest.fixture
def bluez_mock(dbusmock_system: PrivateDBus) -> YieldFixture[dbus.proxies.ProxyObject]:
    template = "bluez5"
    parameters = {
        "advertise": True,
        "passive_scan": True,
    }
    bustype = dbusmock_system.bustype
    server = SpawnedMock.spawn_with_template(
        template, parameters, bustype, stdout=sys.stdout, stderr=sys.stderr
    )
    yield server.obj
    server.terminate()


@pytest.fixture(autouse=True)
def adapter_mock(
    bluez_mock: dbus.proxies.ProxyObject, adapter_name: str
) -> YieldFixture[str]:
    device_name = adapter_name

    # Mock out the DBus adapter
    adapter_alias = "mock-adapter"
    path = bluez_mock.AddAdapter(device_name, adapter_alias)

    assert path == f"/org/bluez/{device_name}"

    # Mock out the non-DBus bits (hci)
    with (
        unittest.mock.patch(
            "bluetooth_adapters.systems.linux.get_adapters_from_hci",
            return_value={0: {"name": device_name, "bdaddr": "00:00:00:00:00:00"}},
        ) as get_adapters_from_hci,  # noqa: F841
        unittest.mock.patch(
            "bluetooth_adapters.systems.linux.USBBluetoothDevice",
        ) as USBBluetoothDevice,  # noqa: F841
        unittest.mock.patch(
            "bluetooth_adapters.systems.linux.isinstance", return_value=False
        ) as isinstance_mock,  # noqa: F841
    ):
        yield path
