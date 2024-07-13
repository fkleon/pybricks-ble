import os

# TODO use pytest.options?
is_bluez_mock = not os.environ.get("DISABLE_BLUEZ_MOCK", False)


pytest_plugins = [
    "tests.fixtures.bluetooth",
]

if is_bluez_mock:
    pytest_plugins += ["dbusmock.pytest_fixtures", "tests.fixtures.bluez5_mock"]


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers",
        "skip_on_bluez_mock(reason): Skip test on BlueZ mock",
    )
