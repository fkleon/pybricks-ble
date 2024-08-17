"""
A pure Python implementation of the Pybricks BLE broadcast/observe message protocol.

Supports the message format first introduced in Pybricks `v3.3.0b5` and updated in `v3.3.0b9`.

Based on:

* [Technical specification](https://github.com/pybricks/technical-info/blob/master/pybricks-ble-broadcast-observe.md) of the message format.
* [Reference implementation](https://github.com/pybricks/pybricks-micropython/blob/v3.3.0/pybricks/common/pb_type_ble.c) in Pybricks.

"""

from enum import IntEnum
from struct import pack, unpack, unpack_from
from typing import Literal, Tuple

from .constants import PybricksBroadcast, PybricksBroadcastValue


def decode_message(
    data: bytes,
) -> PybricksBroadcast:
    """
    Parses a Pybricks broadcast message, typically sourced from
    the BLE advertisement manufacturer data.

    :param data: The encoded data.
    :return: Tuple containing the Pybricks message channel and the
        original value. The original value is either a single object
        or a tuple.
    """

    # idx 0 is the channel
    channel: int = unpack_from("<B", data)[0]  # uint8
    # idx 1 is the message start
    idx = 1
    decoded_data = []
    single_object = False

    while idx < len(data):
        idx, val = _decode_next_value(idx, data)
        if val is None:
            single_object = True
        else:
            decoded_data.append(val)

    if single_object:
        return PybricksBroadcast(channel, decoded_data[0])
    else:
        return PybricksBroadcast(channel, tuple(decoded_data))  # type: ignore # https://github.com/python/mypy/issues/7509


def encode_message(channel: int = 0, *values: PybricksBroadcastValue) -> bytes:
    """
    Encodes the given values as a Pybricks broadcast message.

    :param channel: The Pybricks broadcast channel (0 to 255), defaults to 0.
    :param values: The values to encode in the message.
    :raises ValueError: If the total size of the message exceeds the maximum
        message size of 27 bytes.
    :return: The encoded message.
    """

    # idx 0 is the channel
    encoded_channel = pack("<B", channel)

    # idx 1 is the message start
    encoded_data = bytearray(encoded_channel)

    if len(values) == 1:
        # set SINGLE_OBJECT marker
        header = PybricksBleBroadcastDataType.SINGLE_OBJECT << 5
        encoded_data.append(header)

    for val in values:
        header, encoded_val = _encode_value(val)
        encoded_data.append(header)

        if encoded_val is not None:
            encoded_data += encoded_val

        # max size is 27 bytes: 26 byte payload + 1 byte channel
        if len(encoded_data) > OBSERVED_DATA_MAX_SIZE + 1:
            raise ValueError("payload is restricted to 26 bytes")

    return bytes(encoded_data)


def unpack_pnp_id(data: bytes) -> Tuple[Literal["BT", "USB"], int, int, int]:
    """
    Unpacks raw data from the PnP ID characteristic.

    Implementation sourced from [pybricksdev](https://github.com/pybricks/pybricksdev/blob/v1.0.0-alpha.50/pybricksdev/ble/pybricks.py#L354)
    under the MIT License: Copyright (c) 2018-2023 The Pybricks Authors.

    :param data: The raw data.
    :return: Tuple containing the vendor ID type (`BT` or `USB`), the vendor
        ID, the product ID and the product revision.
    """
    vid_type, vid, pid, rev = unpack("<BHHH", data)
    vid_type = "BT" if vid_type else "USB"
    return vid_type, vid, pid, rev


def pack_pnp_id(
    product_id: int,
    product_rev: int,
    vendor_id_type: Literal["BT", "USB"] = "BT",
    vendor_id: int = 0x0397,
) -> bytes:
    """
    Encodes the PnP ID GATT characteristics.

    :param product_id: The Product ID. Should be a LEGO HubKind.
    :param product_rev: The Product Version.
    :param vendor_id_type: The Vendor ID Source, defaults to `BT`.
    :param vendor_id:  The Vendor ID, defaults to `0x0397` (LEGO).
    :return: The encoded PnP ID.
    """

    pnp_id = pack(
        "<BHHH", 1 if vendor_id_type == "BT" else 0, vendor_id, product_id, product_rev
    )
    return pnp_id


SIZEOF_INT8_T = 1
"""Size of an int8 value in bytes."""
SIZEOF_INT16_T = 2
"""Size of an int16 value in bytes."""
SIZEOF_INT32_T = 4
"""Size of an int32 value in bytes."""

INT_FORMAT = {
    SIZEOF_INT8_T: "<b",
    SIZEOF_INT16_T: "<h",
    SIZEOF_INT32_T: "<i",
}
"""Mapping of integer types to struct format."""

OBSERVED_DATA_MAX_SIZE = 31 - 5
"""Maximum size of the observed data included in the BLE advertising packet:
31 (max adv data size) - 5 (overhead).
"""


class PybricksBleBroadcastDataType(IntEnum):
    """Type codes used for encoding/decoding data."""

    # NB: These values are sent over the air so the numeric values must not be changed.
    # There can be at most 8 types since the values have to fit in 3 bits.

    SINGLE_OBJECT = 0
    """Indicator that the next value is the one and only value (instead of a tuple)."""

    TRUE = 1
    """The Python @c True value."""

    FALSE = 2
    """The Python @c False value."""

    INT = 3
    """The Python @c int type."""

    FLOAT = 4
    """The Python @c float type."""

    STR = 5
    """The Python @c str type."""

    BYTES = 6
    """The Python @c bytes type."""


def _decode_next_value(
    idx: int, data: bytes
) -> tuple[int, None | PybricksBroadcastValue]:
    """
    Decodes the next value in data, starting at ``idx``.

    :param idx: The starting index of the next value in data.
    :param data: The raw data.
    :raises ValueError: If the data type is unsupported.
    :return: Tuple of the next index, and the parsed data.
        The parsed data is ``None`` if this is the
        :py:attr:`PybricksBleBroadcastDataType.SINGLE_OBJECT` marker.
    """

    # data type and size
    type_id = data[idx] >> 5
    size = data[idx] & 0x1F
    data_type = PybricksBleBroadcastDataType(type_id)
    # move cursor to value
    idx += 1

    # data value
    if data_type == PybricksBleBroadcastDataType.SINGLE_OBJECT:
        # Does not contain data by itself, is only used as indicator
        # that the next data is the one and only object
        assert size == 0
        return idx, None
    elif data_type == PybricksBleBroadcastDataType.TRUE:
        assert size == 0
        return idx, True
    elif data_type == PybricksBleBroadcastDataType.FALSE:
        assert size == 0
        return idx, False
    elif data_type == PybricksBleBroadcastDataType.INT:
        # int8 / 1 byte
        # int16 / 2 bytes
        # int32 / 4 bytes
        format = INT_FORMAT[size]
        return idx + size, unpack_from(format, data, idx)[0]
    elif data_type == PybricksBleBroadcastDataType.FLOAT:
        # float / uint32 / 4 bytes
        return idx + size, unpack_from("<f", data, idx)[0]
    elif data_type == PybricksBleBroadcastDataType.STR:
        val = data[idx : idx + size]
        return idx + size, bytes.decode(val)
    elif data_type == PybricksBleBroadcastDataType.BYTES:
        val = data[idx : idx + size]
        return idx + size, val
    else:
        # unsupported data type
        raise ValueError(data_type)


def _encode_value(
    val: PybricksBroadcastValue,
) -> tuple[int, None | bytes]:
    """
    Encodes the given value for a Pybricks broadcast message.

    :param val: The value to encode.
    :raises ValueError: If the data type is unsupported.
    :return: Tuple containing the header byte and the encoded value,
        which may be None if no value is required in addition to the
        header byte.
    """

    size = 0
    encoded_val = None

    if isinstance(val, bool):
        data_type = (
            PybricksBleBroadcastDataType.TRUE
            if val
            else PybricksBleBroadcastDataType.FALSE
        )
    elif isinstance(val, int):
        data_type = PybricksBleBroadcastDataType.INT
        if -128 <= val <= 127:
            # int8
            size = 1
        elif -32768 <= val <= 32767:
            # int16
            size = 2
        else:
            # int32
            size = 4
        format = INT_FORMAT[size]
        encoded_val = pack(format, val)
    elif isinstance(val, float):
        data_type = PybricksBleBroadcastDataType.FLOAT
        size = 4
        encoded_val = pack("<f", val)
    elif isinstance(val, str):
        data_type = PybricksBleBroadcastDataType.STR
        size = len(val)
        encoded_val = val.encode()
    elif isinstance(val, bytes):
        data_type = PybricksBleBroadcastDataType.BYTES
        size = len(val)
        encoded_val = val
    else:
        # unsupported data type
        raise ValueError(type(val))

    header = (data_type << 5) | (size & 0x1F)
    return header, encoded_val
