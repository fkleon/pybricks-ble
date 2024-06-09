"""
This module contains a Pybricks-specific implementation of the BLE "Observer" role.
"""

import logging
from contextlib import AbstractAsyncContextManager
from struct import pack
from typing import (
    Iterable,
    Sequence,
)

from bleak import AdvertisementData, BleakScanner, BLEDevice
from bleak.assigned_numbers import AdvertisementDataType
from bleak.backends.bluezdbus.advertisement_monitor import OrPattern
from bleak.backends.bluezdbus.scanner import BlueZScannerArgs
from cachetools import TTLCache

from ..constants import LEGO_CID
from ..messages import decode_message

log = logging.getLogger(name=__name__)


class BlueZPybricksObserver(AbstractAsyncContextManager):
    """
    A BLE observer backed by BlueZ.

    Keeps a cache of observed Pybricks messages.
    """

    def __init__(
        self,
        channels: Sequence[int] = None,
        rssi_threshold: int | None = None,
        message_ttl: int = 60,
    ):
        self.channels = channels or []
        self.rssi_threshold = rssi_threshold
        self.advertisements = TTLCache(maxsize=len(channels), ttl=message_ttl)

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

        self.scanner = BleakScanner(
            detection_callback=self.callback,
            scanning_mode="passive",
            bluez=BlueZScannerArgs(
                or_patterns=or_patterns,
            ),
        )

    def callback(self, device: BLEDevice, ad: AdvertisementData):
        if self.rssi_threshold is not None and ad.rssi < self.rssi_threshold:
            log.debug("Filtered AD due to RSSI threshold: %i", self.rssi_threshold)
            return

        message = ad.manufacturer_data[LEGO_CID]
        channel, data = decode_message(message)
        log.info("Pybricks broadcast on channel %i: %s", channel, data)
        self.advertisements[channel] = data

    def observe(self, channel: int):
        return self.advertisements[channel]

    async def __aenter__(self):
        log.info("Observing on channels %s...", self.channels or "ALL")
        await self.scanner.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.scanner.stop()
