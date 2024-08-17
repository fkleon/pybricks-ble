"""
Python implementation of the Pybricks BLE broadcast/observe message protocol.

References:
* Technical specification: https://github.com/pybricks/technical-info/blob/master/pybricks-ble-broadcast-observe.md
* Reference implementation: https://github.com/pybricks/pybricks-micropython/blob/v3.3.0b8/pybricks/common/pb_type_ble.c
"""

from enum import IntEnum
from struct import pack, unpack, unpack_from
from typing import Literal, Tuple

from .constants import PybricksBroadcast, PybricksBroadcastValue

SIZEOF_INT8_T = 1
SIZEOF_INT16_T = 2
SIZEOF_INT32_T = 4

INT_FORMAT = {
    SIZEOF_INT8_T: "<b",
    SIZEOF_INT16_T: "<h",
    SIZEOF_INT32_T: "<i",
}


# Type codes used for encoding/decoding data.
class PybricksBleBroadcastDataType(IntEnum):
    # NB: These values are sent over the air so the numeric values must not be changed.
    # There can be at most 8 types since the values have to fit in 3 bits.

    # Indicator that the next value is the one and only value (instead of a tuple). */
    SINGLE_OBJECT = 0
    # The Python @c True value. */
    TRUE = 1
    # The Python @c False value. */
    FALSE = 2
    # The Python @c int type. */
    INT = 3
    # The Python @c float type. */
    FLOAT = 4
    # The Python @c str type. */
    STR = 5
    # The Python @c bytes type. */
    BYTES = 6


# 31 (max adv data size) - 5 (overhead)
OBSERVED_DATA_MAX_SIZE = 31 - 5


def _decode_next_value(
    idx: int, data: bytes
) -> tuple[int, None | PybricksBroadcastValue]:
    """
    Decodes the next value in data, starting at idx.

    Args:
        idx: The starting index of the next value in data.
        data: The raw data.

    Returns:
        Tuple of the next index, and the parsed data.
        The parsed data is None if this is the SINGLE_OBJECT marker.
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


def decode_message(
    data: bytes,
) -> PybricksBroadcast:
    """
    Parses a Pybricks broadcast message, typically sourced from
    the BLE advertisement manufacturer data.

    Args:
        data: The encoded data.

    Returns:
        Tuple containing the Pybricks message channel and the original value.
        The original value is either a single object or a tuple.
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


def _encode_value(
    val: PybricksBroadcastValue,
) -> tuple[int, None | bytes]:
    """
    Encodes the given value for a Pybricks broadcast message.

    Args:
        val: The value to encode.

    Returns:
        Tuple containing the header byte and the encoded value,
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


def encode_message(channel: int = 0, *values: PybricksBroadcastValue) -> bytes:
    """
    Encodes the given values as a Pybricks broadcast message.

    Args:
        channel: The Pybricks broadcast channel (0-255).
        *values: The values to encode in the message.

    Returns:
        The encoded message.

    Raises:
        ValueError: If the total size of the message exceeds the maximum
            message size of 27 bytes.
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
        if len(encoded_data) > 27:
            raise ValueError("payload is restricted to 26 bytes")

    return bytes(encoded_data)


def pack_pnp_id(
    product_id: int,
    product_rev: int,
    vendor_id_type: Literal["BT", "USB"] = "BT",
    vendor_id: int = 0x0397,
) -> bytes:
    """
    Encodes the PnP ID GATT characteristics.

    Args:
        product_id: The Product ID. Should be a LEGO HubKind.
        produce_rev: The Product Version.
        vendor_id_type: The Vendor ID Source. Defaults to 'BT'.
        vendor_id: The Vendor ID. Defaults to 0x0397 (LEGO).

    Returns:
        The encoded message.
    """

    pnp_id = pack(
        "<BHHH", 1 if vendor_id_type == "BT" else 0, vendor_id, product_id, product_rev
    )
    return pnp_id


def unpack_pnp_id(data: bytes) -> Tuple[Literal["BT", "USB"], int, int, int]:
    vid_type, vid, pid, rev = unpack("<BHHH", data)
    vid_type = "BT" if vid_type else "USB"
    return vid_type, vid, pid, rev
