"""
This module contains a Pybricks-specific implementation of the BLE "Observer" role.
"""

import logging
from contextlib import AbstractAsyncContextManager
from struct import pack
from typing import NamedTuple, Sequence

from bleak import AdvertisementData, BleakScanner, BLEDevice
from bleak.assigned_numbers import AdvertisementDataType
from bleak.backends.bluezdbus.advertisement_monitor import OrPattern
from bleak.backends.bluezdbus.scanner import BlueZDiscoveryFilters, BlueZScannerArgs
from cachetools import TTLCache

from ..constants import (
    LEGO_CID,
    PYBRICKS_MAX_CHANNEL,
    PybricksBroadcastData,
    ScanningMode,
)
from ..messages import decode_message

log = logging.getLogger(name=__name__)


class ObservedAdvertisement(NamedTuple):
    """
    Data structure for an observed broadcast.
    """

    data: PybricksBroadcastData
    rssi: int


class BlueZPybricksObserver(AbstractAsyncContextManager):
    """
    A BLE observer backed by BlueZ.

    Keeps a cache of observed Pybricks messages.
    """

    def __init__(
        self,
        scanning_mode: ScanningMode = "passive",
        channels: Sequence[int] | None = None,
        rssi_threshold: int | None = None,
        device_pattern: str | None = "Pybricks",
        message_ttl: int = 60,
    ):
        self.channels = channels or []
        self.rssi_threshold = rssi_threshold
        self.device_pattern = device_pattern
        self.advertisements: TTLCache = TTLCache(
            maxsize=len(self.channels) or PYBRICKS_MAX_CHANNEL, ttl=message_ttl
        )

        # Filters used for active scanning
        filters: BlueZDiscoveryFilters = BlueZDiscoveryFilters()

        if device_pattern:
            filters["Pattern"] = device_pattern
        if rssi_threshold:
            filters["RSSI"] = rssi_threshold

        # Patterns used for passive scanning
        or_patterns: list[OrPattern | tuple[int, AdvertisementDataType, bytes]]

        if self.channels:
            or_patterns = [
                OrPattern(
                    0,
                    AdvertisementDataType.MANUFACTURER_SPECIFIC_DATA,
                    pack("<HB", LEGO_CID, channel),
                )
                for channel in self.channels
            ]
        else:
            or_patterns = [
                OrPattern(
                    0,
                    AdvertisementDataType.MANUFACTURER_SPECIFIC_DATA,
                    pack("<H", LEGO_CID),
                )
            ]

        log.debug(
            "Observer init: scanning_mode=%s, device_pattern=%s, rssi_threshold=%i",
            scanning_mode,
            device_pattern,
            rssi_threshold,
        )

        self.scanner = BleakScanner(
            detection_callback=self.callback,
            scanning_mode=scanning_mode,
            bluez=BlueZScannerArgs(
                filters=filters,
                or_patterns=or_patterns,
            ),
        )

    def callback(self, device: BLEDevice, ad: AdvertisementData):
        if self.rssi_threshold is not None and ad.rssi < self.rssi_threshold:
            log.debug("Filtered AD due to RSSI below threshold: %i", ad.rssi)
            return

        if (ad.local_name and self.device_pattern) and not ad.local_name.startswith(
            self.device_pattern
        ):
            log.debug("Filtered AD due to invalid device name: %s", ad.local_name)
            return

        if LEGO_CID not in ad.manufacturer_data:
            log.debug(
                "Filtered AD due to invalid manufacturer data: %s",
                ad.manufacturer_data.keys(),
            )
            return

        message = ad.manufacturer_data[LEGO_CID]
        channel, data = decode_message(message)

        if self.channels and channel not in self.channels:
            log.debug("Filtered broadcast due to wrong channel: %i", channel)
            return

        log.info(
            "Pybricks broadcast on channel %i: %s (rssi %s)", channel, data, ad.rssi
        )
        self.advertisements[channel] = ObservedAdvertisement(data, ad.rssi)

    def observe(self, channel: int) -> ObservedAdvertisement | None:
        return self.advertisements.get(channel, None)

    async def __aenter__(self):
        log.info("Observing on channels %s...", self.channels or "ALL")
        await self.scanner.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.scanner.stop()
