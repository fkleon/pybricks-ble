"""
A Python implementation of the [Pybricks connectionless Bluetooth messaging][pybricks-message-spec]
protocol.

This package includes the following modules:

- Python implementation of the Pybricks BLE hub interface (`pb_ble.vhub`).
- Observer and Broadcaster for Pybricks BLE messages backed by BlueZ (`pb_ble.bluezdbus`).
- Decoder and Encoder for the Pybricks BLE message format (`pb_ble.messages`).

## Requirements

Pybricks is using Bluetooth Low Energy (BLE) broadcasting advertising packets
to exchange connectionless messages (also known as "BLE Broadcast/Observe").

To use the BLE radio features of this library, you need:

- a BLE-capable Bluetooth adapter.
- a device running Linux with BlueZ and D-Bus (e.g. Ubuntu 20.04 or newer).

To use the BLE observer in passive scanning mode (recommended):

- BlueZ version 5.56 or newer, with [experimental features enabled][bluez-experimental]
    (e.g. Ubuntu 22.04 configured with the bluetoothd `--experimental` flag).

## Usage from the command line

This package includes CLI tools to communicate with Pybricks devices via
connectionless Bluetooth messaging, see `pb_ble.cli` for details and usage.

This is a great way to test your Pybricks programs without having a second
Pybricks Hub available.

It also allows you to check that the connectivity between your device and Pybricks
is going to work as expected before endeavouring further :)

## Usage from Python

- High level: The `get_virtual_ble()` method can be used to configure and
    obtain a high level client object. This object is similar to the Pybricks
    Hub BLE interface, so should feel familiar if you've written a Pybricks
    program already.

- Low level: D-Bus client and service objects defined in `pb_ble.bluezdbus` can
    be used to integrate Pybricks connectionless Bluetooth messaging into
    applications independent from the Pybricks Hub API.

[pybricks-message-spec]:https://github.com/pybricks/technical-info/blob/master/pybricks-ble-broadcast-observe.md
[bluez-experimental]:https://wiki.archlinux.org/title/Bluetooth#Enabling_experimental_features
"""

from .constants import (
    LEGO_CID,
    PybricksBroadcast,
    PybricksBroadcastData,
    PybricksBroadcastValue,
)
from .vhub import VirtualBLE, get_virtual_ble

__all__ = (
    # Core API
    "get_virtual_ble",
    "VirtualBLE",
    "PybricksBroadcast",
    # Submodules
    "vhub",
    "bluezdbus",
    "messages",
    "cli",
)
