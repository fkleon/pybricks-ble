import pytest

from pb_ble import LEGO_CID
from pb_ble.messages import decode_message, encode_message, pack_pnp_id, unpack_pnp_id


class TestPybricksBleDecodeMessage:
    # TODO: Check behaviour against reference implementation
    def test_decode_message_single_object(self):
        # channel 200
        # single object marker
        # int8: 5
        message = b"\xc8\x00\x61\x05"
        channel, data = decode_message(message)

        assert channel == 200
        assert isinstance(data, tuple)
        assert len(data) == 1

        assert data[0] == 5

    # TODO: Check behaviour against reference implementation
    def test_decode_message_single_object_tuple(self):
        # channel 200
        # int8: 5
        message = b"\xc8\x61\x05"
        channel, data = decode_message(message)

        assert channel == 200
        assert isinstance(data, tuple)
        assert len(data) == 1

        assert data[0] == 5

    def test_decode_message_int8_int16_int32(self):
        # channel: 200
        # str: '8_16_32'
        # int8: 127
        # int16: 128
        # int16: 32_767
        # int32: 32_876
        message = b"\xc8\xa78_16_32a\x7fb\x80\x00b\xff\x7fdl\x80\x00\x00"
        channel, data = decode_message(message)

        assert channel == 200
        assert isinstance(data, tuple)
        assert len(data) == 5

        assert data[0] == "8_16_32"
        assert data[1] == 127
        assert data[2] == 128
        assert data[3] == 32_767
        assert data[4] == 32_876

    def test_decode_message_int32_max(self):
        # channel: 200
        # str: 'int32'
        # int32: 536_870_912
        # int32: 1_073_741_823
        message = b"\xc8\xa5int32d\x00\x00\x00 d\xff\xff\xff?"
        channel, data = decode_message(message)

        assert channel == 200
        assert isinstance(data, tuple)
        assert len(data) == 3

        assert data[0] == "int32"
        assert data[1] == 536_870_912
        assert (
            data[2] == 1_073_741_823
        )  # max int32 in micropython seems to be actually int31

    def test_decode_message_float(self):
        # channel: 200
        # str: 'float'
        # float32: PI
        message = b"\xc8\xa5float\x84\xdb\x0fI@"
        channel, data = decode_message(message)

        assert channel == 200
        assert isinstance(data, tuple)
        assert len(data) == 2

        assert data[0] == "float"
        assert data[1] == 3.1415927410125732  # float32 pi

    def test_decode_message_str_bool(self):
        # channel: 200
        # str: 'NTF'
        # bool: True
        # bool: False
        message = b"\xc8\xa3NTF @"
        channel, data = decode_message(message)

        assert channel == 200
        assert isinstance(data, tuple)
        assert len(data) == 3

        assert data[0] == "NTF"
        assert data[1] is True
        assert data[2] is False

    def test_decode_message_bytes(self):
        # channel: 200
        # str: 'bytes'
        # bytes: b'\x00\xc4\x81'
        message = b"\xc8\xa5bytes\xc3\x00\xc4\x81"
        channel, data = decode_message(message)

        assert channel == 200
        assert isinstance(data, tuple)
        assert len(data) == 2

        assert data[0] == "bytes"
        assert data[1] == b"\x00\xc4\x81"

    def test_decode_message_empty(self):
        # channel: 200
        message = b"\xc8"
        channel, data = decode_message(message)

        assert channel == 200
        assert isinstance(data, tuple)
        assert len(data) == 0


class TestPybricksBleEncodeMessage:
    def test_encode_message_single_object(self):
        data = encode_message(200, 5)
        assert data == b"\xc8\x00\x61\x05"

    @pytest.mark.skip("Check behaviour against reference implementation")
    def test_encode_message_single_object_tuple(self):
        data = encode_message(200, (1))
        assert data == b"\xc8\x61\x01"

    def test_encode_message_int8_int16_int32(self):
        data = encode_message(200, "8_16_32", 127, 128, 32_767, 32_876)
        assert data == b"\xc8\xa78_16_32a\x7fb\x80\x00b\xff\x7fdl\x80\x00\x00"

    def test_encode_message_int32_max(self):
        data = encode_message(200, "int32", 536_870_912, 1_073_741_823)
        assert data == b"\xc8\xa5int32d\x00\x00\x00 d\xff\xff\xff?"

    def test_encode_message_float(self):
        data = encode_message(0, "float", 3.1415927410125732)  # float32 pi
        assert data == b"\x00\xa5float\x84\xdb\x0fI@"

    def test_encode_message_str_bool(self):
        data = encode_message(200, "NTF", True, False)
        assert data == b"\xc8\xa3NTF @"

    def test_encode_message_bytes(self):
        data = encode_message(200, "bytes", b"\x00\xc4\x81")
        assert data == b"\xc8\xa5bytes\xc3\x00\xc4\x81"

    def test_encode_message_empty(self):
        data = encode_message(200)
        assert data == b"\xc8"


class TestPybricksBlePnpId:
    def test_pack_pnp_id(self):
        pnp_id = pack_pnp_id(0x00, 0x00, vendor_id_type="BT", vendor_id=LEGO_CID)
        assert pnp_id == b"\x01\x97\x03\x00\x00\x00\x00"

    def test_unpack_pnp_id(self):
        pnp_id = pack_pnp_id(0x00, 0x00, vendor_id_type="BT", vendor_id=LEGO_CID)
        (vid_type, vid, pid, rev) = unpack_pnp_id(pnp_id)
        assert vid_type == "BT"
        assert vid == LEGO_CID
        assert pid == 0x00
        assert rev == 0x00
