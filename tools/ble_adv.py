"""
Parse raw BLE advertisement data
"""
from struct import unpack_from

from bleak.assigned_numbers import AdvertisementDataType
from bluetooth_data_tools import (
    parse_advertisement_data,
)

# Pybricks regular advertisement
# length 49
# {'type': <AdvertisementDataType.FLAGS: 1>, 'length': 2, 'data': b'\x06'}
# {'type': <AdvertisementDataType.INCOMPLETE_LIST_SERVICE_UUID128: 6>, 'length': 17, 'data': b'\xef\xae\xe4Q\x80m\xf4\x89\xdaF\x80\x82\x01\x00\xf5\xc5'}
# {'type': <AdvertisementDataType.TX_POWER_LEVEL: 10>, 'length': 2, 'data': b'\x00'}
# {'type': <AdvertisementDataType.SERVICE_DATA_UUID16: 22>, 'length': 10, 'data': b'P*\x01\x97\x03A\x00\x00\x00'}
# {'type': <AdvertisementDataType.COMPLETE_LOCAL_NAME: 9>, 'length': 13, 'data': b'Pybricks Hub'}
adv_data_hex = "02 01 06 11 06 EF AE E4 51 80 6D F4 89 DA 46 80 82 01 00 F5 C5 02 0A 00 0A 16 50 2A 01 97 03 41 00 00 00 0D 09 50 79 62 72 69 63 6B 73 20 48 75 62"

# Pybricks broadcast
# length 37
# {'type': <AdvertisementDataType.MANUFACTURER_SPECIFIC_DATA: 255>, 'length': 11, 'data': b'\x97\x03\xc8\xa3NTF\x00 @'}
# {'type': <AdvertisementDataType.SERVICE_DATA_UUID16: 22>, 'length': 10, 'data': b'P*\x01\x97\x03A\x00\x00\x00'}
# {'type': <AdvertisementDataType.COMPLETE_LOCAL_NAME: 9>, 'length': 13, 'data': b'Pybricks Hub'}
adv_data_hex = "0B FF 97 03 C8 A3 4E 54 46 00 20 40 0A 16 50 2A 01 97 03 41 00 00 00 0D 09 50 79 62 72 69 63 6B 73 20 48 75 62"

# Pybricks broadcast max length (26 bytes including channel)
# length 56
# {'type': <AdvertisementDataType.MANUFACTURER_SPECIFIC_DATA: 255>, 'length': 30, 'data': b'\x97\x03\xc8\xb926 bytes 26 bytes 26 byte'}
# {'type': <AdvertisementDataType.SERVICE_DATA_UUID16: 22>, 'length': 10, 'data': b'P*\x01\x97\x03A\x00\x00\x00'}
# {'type': <AdvertisementDataType.COMPLETE_LOCAL_NAME: 9>, 'length': 13, 'data': b'Pybricks Hub'}
adv_data_hex = "1E FF 97 03 C8 B9 32 36 20 62 79 74 65 73 20 32 36 20 62 79 74 65 73 20 32 36 20 62 79 74 65 0A 16 50 2A 01 97 03 41 00 00 00 0D 09 50 79 62 72 69 63 6B 73 20 48 75 62"

# PC broadcast
# length 17
# {'type': <AdvertisementDataType.COMPLETE_LOCAL_NAME: 9>, 'length': 16, 'data': b'pybricks_pc_hub'}
adv_data_hex = "10 09 70 79 62 72 69 63 6B 73 5F 70 63 5F 68 75 62"

# PC broadcast including service data
# length 40
# {'type': <AdvertisementDataType.MANUFACTURER_SPECIFIC_DATA: 255>, 'length': 11, 'data': b'\x97\x03\xc8\xa3NTF\x00 @'}
# {'type': <AdvertisementDataType.SERVICE_DATA_UUID16: 22>, 'length': 10, 'data': b'P*\x01\x97\x03\x00\x00\x00\x00'}
# {'type': <AdvertisementDataType.COMPLETE_LOCAL_NAME: 9>, 'length': 16, 'data': b'pybricks_pc_hub'}
adv_data_hex = "0B FF 97 03 C8 A3 4E 54 46 00 20 40 0A 16 50 2A 01 97 03 00 00 00 00 10 09 70 79 62 72 69 63 6B 73 5F 70 63 5F 68 75 62"

# PC broadcast max length
# length 45
# {'type': <AdvertisementDataType.MANUFACTURER_SPECIFIC_DATA: 255>, 'length': 19, 'data': b'\x97\x03\xc8\xb926 bytes 26 by'}
# {'type': <AdvertisementDataType.SERVICE_DATA_UUID16: 22>, 'length': 10, 'data': b'P*\x01\x97\x03\x00\x00\x00\x00'}
# {'type': <AdvertisementDataType.COMPLETE_LOCAL_NAME: 9>, 'length': 13, 'data': b'pybricks_hub'}
adv_data_hex = "13 FF 97 03 C8 B9 32 36 20 62 79 74 65 73 20 32 36 20 62 79 0A 16 50 2A 01 97 03 00 00 00 00 0D 09 70 79 62 72 69 63 6B 73 5F 68 75 62"

# PC broadcast max length manufacturer data 25 bytes
# length 43
# {'type': <AdvertisementDataType.MANUFACTURER_SPECIFIC_DATA: 255>, 'length': 28, 'data': b'\x97\x03\xc8\xb926 bytes 26 bytes 26 by'}
# {'type': <AdvertisementDataType.COMPLETE_LOCAL_NAME: 9>, 'length': 13, 'data': b'pybricks_hub'}
adv_data_hex = "1C FF 97 03 C8 B9 32 36 20 62 79 74 65 73 20 32 36 20 62 79 74 65 73 20 32 36 20 62 79 0D 09 70 79 62 72 69 63 6B 73 5F 68 75 62"

# PC broadcast
# - no includes
# - localname enabled "pb_vhub"
# pb_vhub [] {} {919: b'\x01\x84\xdb\x0fI@'} None
adv_data_hex = "09 FF 97 03 01 84 DB 0F 49 40 08 09 70 62 5F 76 68 75 62"

adv_data_hex = "0E 09 70 79 62 72 69 63 6B 73 5F 76 68 75 62"

# Random broadcast: Buds Live (2x manufacturer data)
adv_data_hex = "02 01 18 1B FF 75 00 42 09 81 02 14 15 04 21 01 49 5C 17 01 17 05 BC AF CF 00 00 00 00 93 00 0A 09 42 75 64 73 20 4C 69 76 65 10 FF 75 00 00 2B 4B A5 C5 66 80 64 63 65 00 01"

adv_data_bin = bytes.fromhex(adv_data_hex)

print(f"Advertisement length: {len(adv_data_bin)}")
ad_sections = []
index = 0

# parse remaining sections
# 37 bytes max
while index < len(adv_data_bin):
    length, ad_type = unpack_from("<BB", adv_data_bin, index)
    index += 1

    # length 2 for length and ad_type
    data = None
    if length > 1:
        data = adv_data_bin[index + 1 : index + length]

    ad_sections.append(
        {"type": AdvertisementDataType(ad_type), "length": length, "data": data}
    )

    index += length

print("Advertisement sections:")
print(*ad_sections, sep="\n", end="\n\n")

adv_data = parse_advertisement_data([adv_data_bin])

print(f"Parsed advertisement: {adv_data}")
print(
    f"Local name: {adv_data.local_name}",
    f"Service UUIDs: {adv_data.service_uuids}",
    f"Service data: {adv_data.service_data}",
    f"Manufacturer data: {adv_data.manufacturer_data}",
    f"TX power: {adv_data.tx_power}",
    sep="\n",
)
