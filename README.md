# Pybricks BLE broadcast client/server

A Python implementation of the [Pybricks Bluetooth Low Energy Broadcast/Observe](https://github.com/pybricks/technical-info/blob/master/pybricks-ble-broadcast-observe.md) message format.

Supports the message format first introduced in Pybricks `v3.3.0b5` and updated in `v3.3.0b9`.

This library also includes CLI tools to communicate with Pybricks devices via BLE data broadcast:
* The BLE broadcaster ("Pybricks server") for sending messages to a Pybricks device.
* The BLE observer ("Pybricks client") for receiving messages from a Pybricks device.

Using the CLI tools requires Python 3.10 on Linux with BlueZ.

## Development

This library requires `bleak >= 0.21.1` which conflicts with the latest `pybricksdev == 1.0.0a46` release.

To work around this, `pybricksdev` is not listed in the project requirements and must be manually installed:

```
pip install -e '.[dev]'
pip install pybricksdev==1.0.0a46 --no-deps
```

## Tools

### BLE broadcaster

Sends Pybricks BLE broadcasts.

Uses `dbus_fast` to create broadcasts via simple BlueZ advertisement services.

Usage:

```
usage: pb_broadcast [-h] [--name NAME] [--timeout TIMEOUT] [--debug] data [data ...]

Send Pybricks BLE broadcasts

positional arguments:
  data               Data to broadcast: channel followed by JSON values

options:
  -h, --help         show this help message and exit
  --name NAME        Bluetooth device name (default: pb_vhub)
  --timeout TIMEOUT  Broadcast timeout (default: 10)
  --debug            Enable debug logging (default: False)
```

### BLE observer

Receives Pybricks BLE broadcasts via `active` or `passive` BLE scanning.

Uses `bleak` for scanning. The recommended scanning mode is `passive` which requires BlueZ >= 5.56 with experimental features enabled.

Usage:

```
usage: pb_observe [-h] [--name NAME] [--rssi [-120 to 0]] [--mode {active,passive}] [--debug] [N [0 to 255] ...]

Observe Pybricks BLE broadcasts

positional arguments:
  N [0 to 255]          Pybricks channels to observe, or all channels if not given. (default: None)

options:
  -h, --help            show this help message and exit
  --name NAME           Bluetooth device name or Bluetooth address for discovery filter (active scan only) (default: Pybricks Hub)
  --rssi [-120 to 0]    RSSI threshold for discovery filter (active scan only) (default: None)
  --mode {active,passive}
                        BLE scanning mode (default: passive)
  --debug               Enable debug logging (default: False)
```
