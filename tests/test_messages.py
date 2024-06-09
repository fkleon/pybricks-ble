import unittest

from pybricksdev.ble.pybricks import unpack_pnp_id  # type: ignore

from pb_ble import LEGO_CID, decode_message, encode_message, pack_pnp_id


class TestPybricksBleDecodeMessage(unittest.TestCase):
    def test_decode_message_single_object(self):
        # channel 200
        # single object marker
        # int8: 5
        message = b"\xc8\x00\x61\x05"
        channel, data = decode_message(message)

        self.assertEqual(channel, 200)
        self.assertEqual(data, 5)

    # TODO: Check behaviour against reference implementation
    def test_decode_message_single_object_tuple(self):
        # channel 200
        # int8: 5
        message = b"\xc8\x61\x05"
        channel, data = decode_message(message)

        self.assertEqual(channel, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], 5)

    def test_decode_message_int8_int16_int32(self):
        # channel: 200
        # str: '8_16_32'
        # int8: 127
        # int16: 128
        # int16: 32_767
        # int32: 32_876
        message = b"\xc8\xa78_16_32a\x7fb\x80\x00b\xff\x7fdl\x80\x00\x00"
        channel, data = decode_message(message)

        self.assertEqual(channel, 200)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0], "8_16_32")
        self.assertEqual(data[1], 127)
        self.assertEqual(data[2], 128)
        self.assertEqual(data[3], 32_767)
        self.assertEqual(data[4], 32_876)

    def test_decode_message_int32_max(self):
        # channel: 200
        # str: 'int32'
        # int32: 536_870_912
        # int32: 1_073_741_823
        message = b"\xc8\xa5int32d\x00\x00\x00 d\xff\xff\xff?"
        channel, data = decode_message(message)

        self.assertEqual(channel, 200)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0], "int32")
        self.assertEqual(data[1], 536_870_912)
        self.assertEqual(
            data[2], 1_073_741_823
        )  # max int32 in micropython seems to be actually int31

    def test_decode_message_float(self):
        # channel: 200
        # str: 'float'
        # float32: PI
        message = b"\xc8\xa5float\x84\xdb\x0fI@"
        channel, data = decode_message(message)

        self.assertEqual(channel, 200)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], "float")
        self.assertEqual(data[1], 3.1415927410125732)  # float32 pi

    def test_decode_message_str_bool(self):
        # channel: 200
        # str: 'NTF'
        # bool: True
        # bool: False
        message = b"\xc8\xa3NTF @"
        channel, data = decode_message(message)

        self.assertEqual(channel, 200)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0], "NTF")
        self.assertEqual(data[1], True)
        self.assertEqual(data[2], False)

    def test_decode_message_bytes(self):
        # channel: 200
        # str: 'bytes'
        # bytes: b'\x00\xc4\x81'
        message = b"\xc8\xa5bytes\xc3\x00\xc4\x81"
        channel, data = decode_message(message)

        self.assertEqual(channel, 200)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], "bytes")
        self.assertEqual(data[1], b"\x00\xc4\x81")

    def test_decode_message_empty(self):
        # channel: 200
        message = b"\xc8"
        channel, data = decode_message(message)

        self.assertEqual(channel, 200)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 0)


class TestPybricksBleEncodeMessage(unittest.TestCase):
    def test_encode_message_single_object(self):
        data = encode_message(200, 5)
        self.assertEqual(data, b"\xc8\x00\x61\x05")

    @unittest.skip("Check behaviour against reference implementation")
    def test_encode_message_single_object_tuple(self):
        data = encode_message(200, (1))
        self.assertEqual(data, b"\xc8\x61\x01")

    def test_encode_message_int8_int16_int32(self):
        data = encode_message(200, "8_16_32", 127, 128, 32_767, 32_876)
        self.assertEqual(data, b"\xc8\xa78_16_32a\x7fb\x80\x00b\xff\x7fdl\x80\x00\x00")

    def test_encode_message_int32_max(self):
        data = encode_message(200, "int32", 536_870_912, 1_073_741_823)
        self.assertEqual(data, b"\xc8\xa5int32d\x00\x00\x00 d\xff\xff\xff?")

    def test_encode_message_float(self):
        data = encode_message(0, "float", 3.1415927410125732)  # float32 pi
        self.assertEqual(data, b"\x00\xa5float\x84\xdb\x0fI@")

    def test_encode_message_str_bool(self):
        data = encode_message(200, "NTF", True, False)
        self.assertEqual(data, b"\xc8\xa3NTF @")

    def test_encode_message_bytes(self):
        data = encode_message(200, "bytes", b"\x00\xc4\x81")
        self.assertEqual(data, b"\xc8\xa5bytes\xc3\x00\xc4\x81")

    def test_encode_message_empty(self):
        data = encode_message(200)
        self.assertEqual(data, b"\xc8")


class TestPybricksBlePnpId(unittest.TestCase):
    def test_pack_pnp_id(self):
        pnp_id = pack_pnp_id(0x00, 0x00, vendor_id_type="BT", vendor_id=LEGO_CID)
        self.assertEqual(pnp_id, b"\x01\x97\x03\x00\x00\x00\x00")

    def test_unpack_pnp_id(self):
        pnp_id = pack_pnp_id(0x00, 0x00, vendor_id_type="BT", vendor_id=LEGO_CID)
        (vid_type, vid, pid, rev) = unpack_pnp_id(pnp_id)
        self.assertEqual(vid_type, "BT")
        self.assertEqual(vid, LEGO_CID)
        self.assertEqual(pid, 0x00)
        self.assertEqual(rev, 0x00)
