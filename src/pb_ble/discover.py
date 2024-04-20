"""
Receive bluetooth advertisements via bleak.
"""

import argparse
import asyncio
import logging
from datetime import datetime
from struct import pack
from typing import Literal

from bleak import BleakScanner
from bleak.assigned_numbers import AdvertisementDataType
from bleak.backends.bluezdbus.advertisement_monitor import OrPattern
from bleak.backends.bluezdbus.scanner import BlueZDiscoveryFilters, BlueZScannerArgs
from pybricksdev.ble.lwp3 import LEGO_CID
from pybricksdev.ble.lwp3.bytecodes import HubKind
from pybricksdev.ble.nus import NUS_SERVICE_UUID
from pybricksdev.ble.pybricks import (
    DI_SERVICE_UUID,
    PNP_ID_UUID,
    PYBRICKS_SERVICE_UUID,
    unpack_pnp_id,
)

from pb_ble import decode_message

log = logging.getLogger(__name__)

service_uuids = [
    "00001800-0000-1000-8000-00805f9b34fb",  # Generic Access
    "00001801-0000-1000-8000-00805f9b34fb",  # Generic Attribute
    "0000180a-0000-1000-8000-00805f9b34fb",  # Standard Device Information Service UUID
    DI_SERVICE_UUID,  # Standard Device Information Service UUID
    "6e400001-b5a3-f393-e0a9-e50e24dcca9e",  # Nordic UART Service (NUS)
    NUS_SERVICE_UUID,  # Nordic UART Service (NUS)
    "c5f50001-8280-46da-89f4-6d8051e4aeef",  # The Pybricks GATT service UUID.
    PYBRICKS_SERVICE_UUID,  # The Pybricks GATT service UUID.
]


async def run(
    channels: list[int],
    scanning_mode: Literal["active", "passive"],
    device_name: str,
    rssi_threshold: int,
):
    or_patterns = None
    filters = None

    # Active scan allows filtering for
    # - device address/name pattern (via discovery filter)
    # - broadcast channel ("software" filter)
    # - local name ("software" filter)
    # - rssi (via discovery filter)
    if scanning_mode == "active":
        # TODO: verify supported filter features
        # Patterns discovery filter requires BlueZ >= 5.54
        filters = BlueZDiscoveryFilters(Pattern=device_name)
        if rssi_threshold is not None:
            filters["RSSI"] = rssi_threshold
        # filters = BlueZDiscoveryFilters(Pattern=bd_name, RSSI=-60)
        # TODO: UUIDs filter returns no results
        # filters = BlueZDiscoveryFilters(UUIDs=[PNP_ID_UUID])
        # filters = BlueZDiscoveryFilters(UUIDs=[PNP_ID_UUID], RSSI=-60)
        # filters = BlueZDiscoveryFilters(UUIDs=[PNP_ID_UUID], Pattern=bd_name, RSSI=-60)
        log.debug("Active scan filters: %r", filters)

    # Passive scan allows filtering for
    # - device address ("software" filter)
    # - broadcast channel (via advertising monitor or_patterns)
    # - rssi ("software" filter)
    if scanning_mode == "passive":
        # TODO: verify scan mode is supported
        # passive scanning on Linux requires BlueZ >= 5.55 with --experimental enabled and Linux kernel >= 5.10
        # Requires BlueZ experimental features enabled
        # filter for manufacturer ID
        # filter for broadcasting channel (first byte of data)
        # only used for passive scanning
        if channels:
            or_patterns = [
                OrPattern(
                    0,
                    AdvertisementDataType.MANUFACTURER_SPECIFIC_DATA,
                    pack("<HB", LEGO_CID, channel),
                )
                for channel in channels
            ]
        else:
            or_patterns = [
                OrPattern(
                    0,
                    AdvertisementDataType.MANUFACTURER_SPECIFIC_DATA,
                    pack("<H", LEGO_CID),
                )
            ]
        # Scan for all devices
        # or_patterns = [
        # BLE_SIG_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE (0x06)
        # OrPattern(0, AdvertisementDataType.FLAGS, b"\x06"),
        # Simultaneous LE and BR/EDR to Same Device
        # OrPattern(0, AdvertisementDataType.FLAGS, b"\x1a"),
        # ]
        log.debug("Passive scan or_patterns: %s", or_patterns)

    async with BleakScanner(
        scanning_mode=scanning_mode,
        bluez=BlueZScannerArgs(
            filters=filters,
            or_patterns=or_patterns,
        ),
    ) as scanner:
        log.info(
            "Observing (%s scan) on channels %s...", scanning_mode, channels or "ALL"
        )

        async for bd, ad in scanner.advertisement_data():
            log.debug("%r with %r", bd, ad)

            # software filters (active):
            # - local name
            # - channel

            # software filters (passive):
            # - bd_address
            # - rssi

            if scanning_mode == "passive":
                # RSSI filter
                if rssi_threshold is not None and ad.rssi < rssi_threshold:
                    log.debug("Filtered AD due to RSSI threshold: %i", rssi_threshold)
                    continue
                # TODO MAC filter
                # TODO verify that name looks like a MAC
                pass
            elif scanning_mode == "active":
                # TODO local name or MAC filter
                pass

            # extra debug
            # only available in active scan
            if PNP_ID_UUID in ad.service_data:
                vendor_id_type, vendor_id, product_id, product_rev = unpack_pnp_id(
                    ad.service_data[PNP_ID_UUID]
                )
                log.debug(
                    "PNP_ID_UUID: %s, %s, %r, %s",
                    vendor_id_type,
                    vendor_id,
                    HubKind(product_id),
                    product_rev,
                )

            # try parsing the broadcast data
            if LEGO_CID in ad.manufacturer_data:
                message = ad.manufacturer_data[LEGO_CID]
                channel, data = decode_message(message)
                if channels and channel not in channels:
                    log.debug("Filtered AD due to incorrect channel: %i", channel)
                    continue

                log.info("Pybricks broadcast on channel %i: %s", channel, data)
            else:
                log.debug(
                    "Filtered AD due to missing manufacturer data: %r",
                    ad.manufacturer_data,
                )
