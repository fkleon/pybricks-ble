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

    The recommended use is as a context manager, which ensures that the
    underlying BLE scanner is stopped when exiting the context:

    ```python
    async with BlueZPybricksObserver(channels=[1, 2, 3]) as observer:
        # Observe for 10 seconds
        await asyncio.sleep(10)
        # Check results for channel 2
        message = observer.observe(2)
        print(message)
    ```
    """

    def __init__(
        self,
        scanning_mode: ScanningMode = "passive",
        channels: Sequence[int] | None = None,
        rssi_threshold: int | None = None,
        device_pattern: str | None = "Pybricks",
        message_ttl: int = 60,
    ):
        """
        Creates a new observer.

        :param scanning_mode: The scanning mode to use, defaults to "passive".
        :param channels: Channels to observe, defaults to None (all channels).
        :param rssi_threshold: Minimum required signal strength of observed
            broadcasts in dBm, defaults to None (no RSSI filtering).
        :param device_pattern: Pattern that the device name of the sender must
            start with, defaults to "Pybricks". Set to `None` to disable filtering.
        :param message_ttl: Time in seconds to cache observed broadcasts for,
            defaults to 60.
        """
        self.channels = channels or []
        """List of channels that this observer is monitoring."""
        self.rssi_threshold = rssi_threshold
        """The configured RSSI threshold for broadcasts."""
        self.device_pattern = device_pattern
        """The configured device name pattern match for broadcasts."""
        self.advertisements: TTLCache = TTLCache(
            maxsize=len(self.channels) or PYBRICKS_MAX_CHANNEL, ttl=message_ttl
        )
        """Cache of observed broadcasts."""

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

        self._scanner = BleakScanner(
            detection_callback=self._callback,
            scanning_mode=scanning_mode,
            bluez=BlueZScannerArgs(
                filters=filters,
                or_patterns=or_patterns,
            ),
        )

    def _callback(self, device: BLEDevice, ad: AdvertisementData):
        """
        @public
        The callback function for detected BLE advertisements from the
        scanner.

        Performs filtering of advertisements, decodes the Pybricks
        broadcast message contained in the advertisement, and stores
        it in the broadcast cache.

        Depending on the selected scanning mode, certain filters must
        be applied here:

        1. Filter advertisements based on the configured `rssi_threshold`
            and `device_pattern` (required in "passive" mode).
        2. Filter advertisements that contain invalid manufacturer data,
            such as non-Pybricks advertisements (required in "active" mode).
        4. Filter messages on the incorrect Pybricks channel (required in
            "active" mode).

        :param device: The device sending the advertisement.
        :param ad: The advertisement data.
        """
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
        """
        Retrieves the last observed data for a given channel.

        :param channel: The channel to observe (0 to 255).
        :return: The received data in the same format as it was sent, or `None`
            if no recent data is available.
        """
        return self.advertisements.get(channel, None)

    async def __aenter__(self):
        log.info("Observing on channels %s...", self.channels or "ALL")
        await self._scanner.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._scanner.stop()
