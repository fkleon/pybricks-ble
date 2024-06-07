# Pybricks BLE broadcast client/server

A Python implementation of the [Pybricks Bluetooth Low Energy Broadcast/Observe](https://github.com/pybricks/technical-info/blob/master/pybricks-ble-broadcast-observe.md) message format.

Supports the message format first introduced in Pybricks `v3.3.0b5` and updated in `v3.3.0b9`.

This library also includes CLI tools to communicate with Pybricks devices via BLE data broadcast:
* The BLE broadcaster ("Pybricks server") for sending messages to a Pybricks device.
* The BLE observer ("Pybricks client") for receiving messages from a Pybricks device.

Using the CLI tools requires Python 3.10 on Linux with BlueZ.

## Development

```
pip install -e '.[dev]'
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

Receives Pybricks BLE broadcasts via `passive` BLE scanning.

Uses `bleak` for scanning and requires BlueZ >= 5.56 with experimental features enabled.

Usage:

```
usage: pb_observe [-h] [--rssi [-120 to 0]] [--debug] [N [0 to 255] ...]

Observe Pybricks BLE broadcasts

positional arguments:
  N [0 to 255]        Pybricks channels to observe, or all channels if not given. (default: None)

options:
  -h, --help          show this help message and exit
  --rssi [-120 to 0]  RSSI threshold (default: None)
  --debug             Enable debug logging (default: False)
```
