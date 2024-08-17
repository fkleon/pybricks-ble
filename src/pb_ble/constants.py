from __future__ import annotations

from typing import Literal, NamedTuple, TypeAlias

LEGO_CID = 0x0397
"""LEGO System A/S company identifier."""

PYBRICKS_MAX_CHANNEL = 255  # uint8
"""Highest channel supported by Pybricks broadcast/observe messages"""

ScanningMode: TypeAlias = Literal["active", "passive"]
"""Supported scanning modes for observing broadcasts."""

# Type aliases
PybricksBroadcastValue: TypeAlias = bool | int | float | str | bytes
"""Type of a value that can be broadcast."""

PybricksBroadcastData: TypeAlias = (
    PybricksBroadcastValue | tuple[PybricksBroadcastValue]
)
"""Type of the broadcast data."""


class PybricksBroadcast(NamedTuple):
    """
    Data structure for a Pybricks broadcast.
    """

    channel: int
    """The broadcast channel for the data (0 to 255)."""

    data: PybricksBroadcastData
    """The value or values to be broadcast."""
