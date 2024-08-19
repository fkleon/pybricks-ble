"""
Command line tools to communicate with Pybricks devices via
connectionless Bluetooth messaging:

- The [Pybricks BLE broadcaster](#ble-broadcaster) for **sending messages** to a Pybricks device (`pb_ble.cli.broadcast`).
- The [Pybricks BLE observer](#ble-observer) for **receiving messages** from a Pybricks device (`pb_ble.cli.observe`).

## BLE broadcaster

`pb_broadcast` is a CLI tool to send Pybricks BLE broadcasts.

### Example

To broadcast the values `"pybricks"`, `True` and `1.0` on channel 0:

```sh
pb_broadcast 0 \"pybricks\" true 1.0
```

The default timeout is 10 seconds, after which the advertisement is stopped.
To broadcast for an unlimited time, use `--timeout 0`.

### Usage

```
usage: pb_broadcast [-h] [--name NAME] [--timeout TIMEOUT] [--debug] data [data ...]

Send Pybricks BLE broadcasts

positional arguments:
  data               Data to broadcast: channel followed by JSON values

options:
  -h, --help         show this help message and exit
  --name NAME        Bluetooth device name to use for advertisements (default: pb_vhub)
  --timeout TIMEOUT  Broadcast timeout in seconds (default: 10)
  --debug            Enable debug logging (default: False)
```

## BLE observer

`pb_observe` is a CLI tool to receive Pybricks BLE broadcasts via `passive` or `active` BLE scanning.

- Passive scanning is the default and recommended, but requires BlueZ >= 5.56 with [experimental features enabled][bluez-experimental].
- Active scanning is provided as a well-supported fallback. It may negatively impact the power consumption of nearby BLE devices.

### Example

To observe broadcasts on channel 1 and 2:

```sh
pb_observe 1 2
```

To enable active scanning, use `--mode active`.

### Usage

```
usage: pb_observe [-h] [--rssi [-120 to 0]] [--pattern PATTERN] [--mode {active,passive}] [--debug] [N [0 to 255] ...]

Observe Pybricks BLE broadcasts

positional arguments:
  N [0 to 255]          Pybricks channels to observe, or all channels if not given. (default: None)

options:
  -h, --help            show this help message and exit
  --rssi [-120 to 0]    RSSI threshold (default: None)
  --pattern PATTERN     Device name pattern filter (default: Pybricks)
  --mode {active,passive}
                        BLE scanning mode (default: passive)
  --debug               Enable debug logging (default: False)
```

[bluez-experimental]:https://wiki.archlinux.org/title/Bluetooth#Enabling_experimental_features
"""

import datetime
import logging
import sys

if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="[%(asctime)s] [%(name)-20s] [%(levelname)-8s] %(message)s",
    )

    # ISO8601 dateformat for logging including milliseconds
    logging.Formatter.formatTime = (
        lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(
            record.created, datetime.timezone.utc
        )
        .astimezone()
        .isoformat(sep="T", timespec="milliseconds")
    )

__all__ = ()
