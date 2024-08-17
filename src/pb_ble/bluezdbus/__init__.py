"""
BlueZ-backed implementations of BLE observer and BLE broadcaster roles.

High level API:

- `BlueZBroadcaster`: A generic BLE broadcaster.
- `BlueZPybricksObserver`: A specialised BLE observer for Pybricks messages.

Generic D-Bus bindings:

- `LEAdvertisement`: Service implementation of the [org.bluez.LEAdvertisement1][]
    D-Bus interface and the following specialisations:
  - `BroadcastAdvertisement`: A BLE broadcast advertisement.
  - `PybricksBroadcastAdvertisement`: A Pybricks broadcast advertisement.
- `LEAdvertisingManager`: Client implementation of the [org.bluez.LEAdvertisingManager1][] D-Bus interface.

The D-Bus bindings are implemented with the [dbus-fast][] library.

[org.bluez.LEAdvertisement1]:https://github.com/bluez/bluez/blob/5.75/doc/org.bluez.LEAdvertisement.rst
[org.bluez.LEAdvertisingManager1]:https://github.com/bluez/bluez/blob/5.75/doc/org.bluez.LEAdvertisingManager.rst
[dbus-fast]:https://github.com/Bluetooth-Devices/dbus-fast
"""

from .adapters import get_adapter, get_adapter_details
from .advertisement import (
    BroadcastAdvertisement,
    Capability,
    Feature,
    Include,
    LEAdvertisement,
    LEAdvertisingManager,
    PybricksBroadcastAdvertisement,
    SecondaryChannel,
    Type,
)
from .broadcaster import BlueZBroadcaster
from .observer import BlueZPybricksObserver, ObservedAdvertisement

__all__ = (
    # High level objects
    "BlueZBroadcaster",
    "BlueZPybricksObserver",
    "ObservedAdvertisement",
    # D-Bus bindings
    "LEAdvertisement",
    "BroadcastAdvertisement",
    "PybricksBroadcastAdvertisement",
    "LEAdvertisingManager",
    # D-Bus constants
    "Type",
    "Include",
    "Capability",
    "Feature",
    "SecondaryChannel",
)
