# pb_ble

A Python implementation of the [Pybricks connectionless Bluetooth messaging](https://github.com/pybricks/technical-info/blob/master/pybricks-ble-broadcast-observe.md) protocol.

## What is this?

This package was born from the need to develop, test and debug Pybricks programs that make use of connectionless messaging -- but without having a second (or third..) Pybricks Hub readily available.

It includes both command line tools and Python interfaces to send and receive Pybricks broadcast messages on a device running Linux.

To use the Bluetooth Low Energy (BLE) radio features of this library, you need:

- a BLE-capable Bluetooth adapter.
- a device running Linux with BlueZ and D-Bus (e.g. Ubuntu 20.04 or newer).

📝 Find out more in the [documentation](https://portfolio.leonhardt.co.nz/pybricks-ble)!

### Alternatives

If you're running a SBC or board that's Micropython-capable, check out [micropython-bleradio](https://github.com/pybricks/micropython-bleradio) from the Pybricks creators.

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

Running the unit tests requires a system with D-Bus.

```sh
make test
```

#### Integration tests

Running the integration tests requires a system with D-Bus, BlueZ and a powered BLE-capable Bluetooth device.

These tests interface with BlueZ directly, so will trigger actual Bluetooth advertisements to be sent for a short time.

```sh
make integration-test
```

### Documentation

A web version of the documentation is generated with [pdoc](https://pdoc.dev/).

To run this locally:

```sh
make -C docs/ dev
```