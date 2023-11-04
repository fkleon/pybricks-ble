# Pybricks BLE broadcast client/server

A Python implementation of the [Pybricks Bluetooth Low Energy Broadcast/Observe](https://github.com/pybricks/technical-info/blob/master/pybricks-ble-broadcast-observe.md) message format.

This library also includes tools to enable BLE broadcast communication between Pybricks and a PC:
* The BLE broadcaster ("Pybricks server") for sending messages to a Pybricks device.
* The BLE observer ("Pybricks client") for receiving messages from a Pybricks device.

This requires Python 3.10 on Linux with BlueZ (experimental features recommended).

Note: Supports the message format introduced in Pybricks `v3.3.0b5`, but **does not support** the updated message format from Pybricks `v3.3.0b9`.

## BLE broadcaster

Sends Pybricks BLE broadcasts.

Uses `dbus_fast` to create broadcasts via simple BlueZ advertisement services.

Usage:

```
usage: pb_broadcast [-h] [--name NAME] [--timeout TIMEOUT] [--debug]

Send Pybricks BLE broadcasts

options:
  -h, --help            show this help message and exit
  --name NAME           Bluetooth device name
  --timeout TIMEOUT     Broadcast timeout
  --debug               Enable debug logging
```

### BLE observer

Receives Pybricks BLE broadcasts via `active` or `passive` BLE scanning.

Uses `bleak` for scanning. The recommended scanning mode is `passive` which requires BlueZ >= v5.64 with experimental features enabled.

Usage:

```
usage: pb_observe [-h] [--name NAME] [--rssi [-120 to 0]] [--mode {active,passive}] [--debug] [N [0 to 255] ...]

Observe Pybricks BLE broadcasts

positional arguments:
  N [0 to 255]          Pybricks channels to observe

options:
  -h, --help            show this help message and exit
  --name NAME           Bluetooth device name or Bluetooth address for discovery filter
  --rssi [-120 to 0]    RSSI threshold for discovery filter
  --mode {active,passive}
                        BLE scanning mode
  --debug               Enable debug logging
```
