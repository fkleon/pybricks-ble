# Pybricks BLE broadcast client/server

A Python implementation of the [Pybricks Bluetooth Low Energy Broadcast/Observe](https://github.com/pybricks/technical-info/blob/master/pybricks-ble-broadcast-observe.md) message format.

Supports the message format first introduced in Pybricks `v3.3.0b5` and updated in `v3.3.0b9`.

This library also includes [CLI tools](#tools) to communicate with Pybricks devices via BLE data broadcast:
* The BLE broadcaster ("Pybricks server") for sending messages to a Pybricks device.
* The BLE observer ("Pybricks client") for receiving messages from a Pybricks device.

Using the CLI tools requires Python 3.10 on Linux with BlueZ.

## Development

A `Makefile` is provided for convenience. Running one of the provided targets will create or refresh a local Python virtual environment:

* `format`: Format the code base.
* `lint`: Lint the code base.
* `typecheck`: Type-check the code base.

Alternatively, use `pip` for an editable installation of this library:

```
pip install -e '.[dev]'
```

### Testing

There are two test modes:

* unit test (default): run the test suite against a BlueZ mock service.
* integration test: run the tests suite against the real BlueZ service on your system.

#### Unit tests

Running the unit tests requires a system with DBus.

```sh
make test
```

#### Integration tests

Running the integration tests requires a system with DBus, BlueZ and a powered BLE-capable Bluetooth device.

These tests interface with BlueZ directly, so will trigger actual Bluetooth advertisements to be sent for a short time.

```sh
make integration-test
```

## Tools

### BLE broadcaster

Sends Pybricks BLE broadcasts.

Uses `dbus_fast` to create broadcasts via simple BlueZ advertisement services.

#### Examples

Broadcast the values `"pybricks"`, `True` and `1.0` on channel 0:

```sh
pb_broadcast 0 \"pybricks\" true 1.0
```

#### Usage

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

### BLE observer

Receives Pybricks BLE broadcasts via `passive` BLE scanning.

Uses `bleak` for scanning and requires BlueZ >= 5.56 with experimental features enabled.

#### Examples

Observe broadcasts on channel 1 and 2:

```sh
pb_observe 1 2
```

#### Usage

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
