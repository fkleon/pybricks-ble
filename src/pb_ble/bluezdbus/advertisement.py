"""
Advertisement API
---------------------

This module contains types associated with the BlueZ D-Bus advertisement api:

- [org.bluez.LEAdvertisement](https://github.com/bluez/bluez/blob/5.75/doc/org.bluez.LEAdvertisement.rst)
- [org.bluez.LEAdvertisingManager](https://github.com/bluez/bluez/blob/5.75/doc/org.bluez.LEAdvertisingManager.rst)
"""

import logging
from enum import Enum
from typing import (
    Any,
    Callable,
    no_type_check,
    overload,
)

from dbus_fast.aio import ProxyInterface, ProxyObject
from dbus_fast.constants import PropertyAccess
from dbus_fast.service import ServiceInterface, _Property, dbus_property, method
from dbus_fast.signature import Variant

from ..constants import (
    LEGO_CID,
    PybricksBroadcastData,
)
from ..messages import decode_message, encode_message

logger = logging.getLogger(__name__)


class Type(Enum):
    """LEAdvertisement: Type"""

    BROADCAST = "broadcast"
    PERIPHERAL = "peripheral"


class Include(Enum):
    """LEAdvertisingManager: SupportedIncludes"""

    TX_POWER = "tx-power"
    APPEARANCE = "appearance"
    LOCAL_NAME = "local-name"
    RSI = "rsi"


class SecondaryChannel(Enum):
    """LEAdvertisingManager: SupportedSecondaryChannels"""

    ONE = "1M"
    TWO = "2M"
    CODED = "Coded"


class Capability(Enum):
    MAX_ADV_LEN = "MaxAdvLen"
    """Max advertising data length [byte]"""

    MAX_SCN_RSP_LEN = "MaxScnRspLen"
    """Max advertising scan response length [byte]"""

    MIN_TX_POWER = "MinTxPower"
    """Min advertising tx power (dBm) [int16]"""

    MAX_TX_POWER = "MaxTxPower"
    """Max advertising tx power (dBm) [int16]"""


class Feature(Enum):
    """LEAdvertisingManager: SupportedFeatures"""

    CAN_SET_TX_POWER = "CanSetTxPower"
    """Indicates whether platform can specify tx power on each advertising instance."""

    HARDWARE_OFFLOAD = "HardwareOffload"
    """Indicates whether multiple advertising will be offloaded to the controller."""


class LEAdvertisement(ServiceInterface):
    """
    Implementation of the `org.bluez.LEAdvertisement1` D-Bus interface.
    """

    INTERFACE_NAME: str = "org.bluez.LEAdvertisement1"

    def __init__(
        self,
        advertising_type: Type,
        local_name: str,
        index: int = 0,
        includes: set[Include] = set(),
    ):
        if index < 0:
            raise ValueError("index must be positive")

        self.index = index
        self.path = f"/org/bluez/{local_name}/advertisement{index:03}"

        self._type: str = advertising_type.value
        self._service_uuids: list[str] = []
        self._manufacturer_data: dict[int, bytes] = {}  # uint16 -> bytes
        self._solicit_uuids: list[str] = []
        self._service_data: dict[str | int, bytes] = {}  # uint16 | str -> bytes
        self._data: dict[int, bytes] = {}  # EXPERIMENTAL # uint8 -> bytes
        self._discoverable: bool = False  # EXPERIMENTAL
        self._discoverable_timeout: int = 0  # EXPERIMENTAL # uint16
        self._includes: list[str] = [i.value for i in includes]
        self._local_name: str = local_name
        self._appearance: int = 0x00  # uint16
        self._duration: int = 2  # uint16
        self._timeout: int = 0  # uint16
        self._secondary_channel: str = SecondaryChannel.ONE.value  # EXPERIMENTAL
        self._min_interval: int = 100  # EXPERIMENTAL # uint32
        self._max_interval: int = 1000  # EXPERIMENTAL # uint32
        self._tx_power: int = 7  # EXPERIMENTAL # int16

        super().__init__(self.INTERFACE_NAME)

    def _enable_props(self, *prop_names: str):
        """
        Enables the given properties.

        This should be used by subclasses to opt-into experimental properties.

        :param prop_names: List of D-Bus property names to enable.
        :raises ValueError: If an unknown property was passed.
        """
        for prop_name in prop_names:
            prop: _Property | None = next(
                (
                    p
                    for p in ServiceInterface._get_properties(self)
                    if p.name == prop_name
                ),
                None,
            )
            if prop is None:
                raise ValueError(f"Unknown property: {prop_name}")
            else:
                prop.disabled = False

    def _disable_props(self, *prop_names: str):
        """
        Disables the given properties.

        This can be used by subclasses to opt-out of exposing certain properties.

        :param prop_names: List of D-Bus property names to disable.
        :raises ValueError: If an unknown property was passed.
        """
        for prop_name in prop_names:
            prop: _Property | None = next(
                (
                    p
                    for p in ServiceInterface._get_properties(self)
                    if p.name == prop_name
                ),
                None,
            )
            if prop is None:
                raise ValueError(f"Unknown property: {prop_name}")
            else:
                prop.disabled = True

    @method()
    def Release(self):
        logger.debug("Released advertisement: %s", self)

    @dbus_property(access=PropertyAccess.READ)
    @no_type_check
    def Type(self) -> "s":  # type: ignore # noqa: F821
        """
        Determines the type of advertising packet requested.
        """
        return self._type

    @Type.setter  # type: ignore
    @no_type_check
    def Type(self, type: "s"):  # type: ignore  # noqa: F821
        self._type = type

    @dbus_property()
    @no_type_check
    def ServiceUUIDs(self) -> "as":  # type: ignore # noqa: F821 F722
        """
        List of UUIDs to include in the "Service UUID" field of the Advertising Data.
        """
        return self._service_uuids

    @ServiceUUIDs.setter  # type: ignore
    @no_type_check
    def ServiceUUIDs(self, service_uuids: "as"):  # type: ignore # noqa: F821 F722
        self._service_uuids = service_uuids

    @dbus_property()
    @no_type_check
    def ManufacturerData(self) -> "a{qv}":  # type: ignore # noqa: F821 F722
        """
        Manufacturer Data fields to include in the Advertising Data.
        Keys are the Manufacturer ID to associate with the data.
        """
        return self._manufacturer_data

    @ManufacturerData.setter  # type: ignore
    @no_type_check
    def ManufacturerData(self, data: "a{qv}"):  # type: ignore # noqa: F821 F722
        self._manufacturer_data = data

    @dbus_property()
    @no_type_check
    def SolicitUUIDs(self) -> "as":  # type: ignore # noqa: F821 F722
        """
        Array of UUIDs to include in "Service Solicitation" Advertisement Data.
        """
        return self._solicit_uuids

    @SolicitUUIDs.setter  # type: ignore
    @no_type_check
    def SolicitUUIDs(self, uuids: "as"):  # type: ignore # noqa: F821 F722
        self._solicit_uuids = uuids

    @dbus_property()
    @no_type_check
    def ServiceData(self) -> "a{sv}":  # type: ignore # noqa: F821 F722
        """
        Service Data elements to include. The keys are the UUID to associate with the data.
        """
        return self._service_data

    @ServiceData.setter  # type: ignore
    @no_type_check
    def ServiceData(self, data: "a{sv}"):  # type: ignore # noqa: F821 F722
        self._service_data = data

    @dbus_property(disabled=True)
    @no_type_check
    def Data(self) -> "a{yv}":  # type: ignore # noqa: F821 F722
        """
        Advertising Data to include.
        Key is the advertising type and value is the data as byte array.
        """
        return self._data

    @Data.setter  # type: ignore
    @no_type_check
    def Data(self, data: "a{yv}"):  # type: ignore # noqa: F821 F722
        self._data = data

    @dbus_property(disabled=True)
    @no_type_check
    def Discoverable(self) -> "b":  # type: ignore # noqa: F821 F722
        """
        Advertise as general discoverable.
        When present this will override adapter Discoverable property.
        """
        return self._discoverable

    @Discoverable.setter  # type: ignore
    @no_type_check
    def Discoverable(self, discoverable: "b"):  # type: ignore # noqa: F821 F722
        self._discoverable = discoverable

    @dbus_property(disabled=True)
    @no_type_check
    def DiscoverableTimeout(self) -> "q":  # type: ignore # noqa: F821 F722
        """
        The discoverable timeout in seconds.
        A value of zero means that the timeout is disabled and it will stay in discoverable/limited mode forever.
        """
        return self._discoverable_timeout

    @DiscoverableTimeout.setter  # type: ignore
    @no_type_check
    def DiscoverableTimeout(self, timeout: "q"):  # type: ignore # noqa: F821 F722
        self._discoverable_timeout = timeout

    @dbus_property()
    @no_type_check
    def Includes(self) -> "as":  # type: ignore # noqa: F821 F722
        """
        List of features to be included in the advertising packet.
        """
        return self._includes

    @Includes.setter  # type: ignore
    @no_type_check
    def Includes(self, includes: "as"):  # type: ignore # noqa: F821 F722
        self._includes = includes

    @dbus_property()
    @no_type_check
    def LocalName(self) -> "s":  # type: ignore # noqa: F821 N802
        """
        Local name to be used in the advertising report.
        If the string is too big to fit into the packet it will be truncated.
        """
        return self._local_name

    @LocalName.setter  # type: ignore
    @no_type_check
    def LocalName(self, name: "s"):  # type: ignore # noqa: F821 N802
        self._local_name = name

    @dbus_property()
    @no_type_check
    def Appearance(self) -> "q":  # type: ignore # noqa: F821 N802
        """
        Appearance to be used in the advertising report.
        """
        return self._appearance

    @Appearance.setter  # type: ignore
    @no_type_check
    def Appearance(self, appearance: "q"):  # type: ignore # noqa: F821 N802
        self._appearance = appearance

    @dbus_property()
    @no_type_check
    def Duration(self) -> "q":  # type: ignore # noqa: F821 N802
        """
        Rotation duration of the advertisement in seconds.
        If there are other applications advertising no duration is set the default is 2 seconds.
        """
        return self._duration

    @Duration.setter  # type: ignore
    @no_type_check
    def Duration(self, seconds: "q"):  # type: ignore # noqa: F821 N802
        self._duration = seconds

    @dbus_property()
    @no_type_check
    def Timeout(self) -> "q":  # type: ignore # noqa: F821 N802
        """
        Timeout of the advertisement in seconds.
        This defines the lifetime of the advertisement.
        """
        return self._timeout

    @Timeout.setter  # type: ignore
    @no_type_check
    def Timeout(self, seconds: "q"):  # type: ignore # noqa: F821 N802
        self._timeout = seconds

    @dbus_property(disabled=True)
    @no_type_check
    def SecondaryChannel(self) -> "s":  # type: ignore # noqa: F821 N802
        """
        Secondary channel to be used.
        Primary channel is always set to "1M" except when "Coded" is set.
        """
        return self._secondary_channel

    @SecondaryChannel.setter  # type: ignore
    @no_type_check
    def SecondaryChannel(self, channel: "q"):  # type: ignore # noqa: F821 N802
        self._secondary_channel = channel

    @dbus_property(disabled=True)
    @no_type_check
    def MinInterval(self) -> "u":  # type: ignore # noqa: F821 N802
        """
        Minimum advertising interval to be used by the advertising set, in milliseconds.
        Acceptable values are in the range [20ms, 10,485s].
        If the provided MinInterval is larger than the provided MaxInterval,
        the registration will return failure.
        """
        return self._min_interval

    @MinInterval.setter  # type: ignore
    @no_type_check
    def MinInterval(self, milliseconds: "u"):  # type: ignore # noqa: F821 N802
        self._min_interval = milliseconds

    @dbus_property(disabled=True)
    @no_type_check
    def MaxInterval(self) -> "u":  # type: ignore # noqa: F821 N802
        """
        Maximum advertising interval to be used by the advertising set, in milliseconds.
        Acceptable values are in the range [20ms, 10,485s].
        If the provided MinInterval is larger than the provided MaxInterval,
        the registration will return failure.
        """
        return self._max_interval

    @MaxInterval.setter  # type: ignore
    @no_type_check
    def MaxInterval(self, milliseconds: "u"):  # type: ignore # noqa: F821 N802
        self._max_interval = milliseconds

    @dbus_property(disabled=True)
    @no_type_check
    def TxPower(self) -> "n":  # type: ignore # noqa: F821 N802
        """
        Requested transmission power of this advertising set.
        The provided value is used only if the "CanSetTxPower" feature is enabled on the org.bluez.LEAdvertisingManager(5).
        The provided value must be in range [-127 to +20], where units are in dBm.
        """
        return self._tx_power

    @TxPower.setter  # type: ignore
    @no_type_check
    def TxPower(self, dbm: "n"):  # type: ignore # noqa: F821 N802
        self._tx_power = dbm


class BroadcastAdvertisement(LEAdvertisement):
    """
    Implementation of a broadcast advertisement.

    This sets the advertising type to "broadcast" and toggles
    available properties appropriately.
    """

    def __init__(
        self,
        local_name: str,
        index: int = 0,
        on_release: Callable[[str], None] = lambda path: None,
    ):
        super().__init__(
            Type.BROADCAST,
            local_name,
            index,
            # set([Include.LOCAL_NAME]),
        )

        self.on_release: Callable[[str], None] = on_release
        """Callback function that is called when this advertisement is released by BlueZ."""

        # Disable properties that aren't needed for broadcasting
        self._disable_props(
            "ServiceUUIDs",
            "SolicitUUIDs",
            "LocalName",
            "Appearance",
            "Duration",
        )
        # Enable experimental properties useful for broadcasting
        self._enable_props("MinInterval", "MaxInterval", "TxPower")

        # for prop in ServiceInterface._get_properties(self):
        #    logger.debug("Property %s (%s)", prop.name, "DISABLED" if prop.disabled else "ENABLED")

    @method()
    def Release(self):
        super().Release()
        self.on_release(self.path)


class PybricksBroadcastAdvertisement(BroadcastAdvertisement):
    """
    Implementation of a Pybricks broadcast advertisement.

    The data to broadcast is set via the message property.
    """

    LEGO_CID = LEGO_CID
    """LEGO System A/S company identifier."""

    def __init__(
        self,
        local_name: str,
        channel: int = 0,
        data: PybricksBroadcastData | None = None,
        on_release: Callable[[str], None] = lambda path: None,
    ):
        super().__init__(local_name, channel, on_release)
        if data:
            self.message = data

    @property
    def channel(self) -> int:
        """The channel of this broadcast message."""
        return self.index

    @property
    def message(self) -> PybricksBroadcastData | None:
        """The data contained in this broadcast message."""
        if self.LEGO_CID in self._manufacturer_data:
            channel, value = decode_message(
                self._manufacturer_data[self.LEGO_CID].value  # type: ignore
            )
            return value
        else:
            return None

    @message.setter
    def message(self, value: PybricksBroadcastData):
        value = value if isinstance(value, tuple) else (value,)
        message = encode_message(self.channel, *value)
        self._manufacturer_data[self.LEGO_CID] = Variant("ay", message)  # type: ignore
        # Notify BlueZ of the changed manufacturer data so the advertisement is updated
        self.emit_properties_changed(
            changed_properties={"ManufacturerData": self._manufacturer_data}
        )

    def __str__(self):
        return f"PybricksBroadcastAdvertisement(channel={self.channel}, data={self.message!r}, timeout={self._timeout})"


class LEAdvertisingManager:
    """
    Client implementation of the `org.bluez.LEAdvertisementManager1` D-Bus interface.
    """

    INTERFACE_NAME: str = "org.bluez.LEAdvertisingManager1"

    def __init__(
        self,
        adapter: ProxyObject | None = None,
        adv_manager: ProxyInterface | None = None,
    ):
        if adapter is None and adv_manager is None:
            raise ValueError("adapter or adv_manager required")

        self._adv_manager = adv_manager or adapter.get_interface(self.INTERFACE_NAME)  # type: ignore

    async def register_advertisement(
        self, adv: LEAdvertisement, options: dict | None = None
    ):
        """
        Registers an advertisement object to be sent over the LE Advertising channel.
        The service must implement `org.bluez.LEAdvertisement1` interface.

        :param adv: The advertisement service object.
        :param options: Advertisement options, defaults to None.
        :return: `None`
        """
        options = options or {}
        return await self._adv_manager.call_register_advertisement(adv.path, options)  # type: ignore

    @overload
    async def unregister_advertisement(self, adv: LEAdvertisement): ...
    @overload
    async def unregister_advertisement(self, adv: str): ...
    async def unregister_advertisement(self, adv):
        """
        Unregisters an advertisement that has been previously registered using `register_advertisement()`.
        The object path parameter must match the same value that has been used on registration.

        :param adv: The advertisement service object, or path.
        :return: `None`
        """
        if isinstance(adv, str):
            return await self._adv_manager.call_unregister_advertisement(adv)  # type: ignore
        else:
            return await self._adv_manager.call_unregister_advertisement(adv.path)  # type: ignore

    async def active_instances(self) -> int:
        """Number of active advertising instances."""
        return await self._adv_manager.get_active_instances()  # type: ignore

    async def supported_instances(self) -> int:
        """Number of available advertising instances."""
        return await self._adv_manager.get_supported_instances()  # type: ignore

    async def supported_includes(self) -> list[Include]:
        """List of supported system includes."""
        return await self._adv_manager.get_supported_includes()  # type: ignore

    async def supported_secondary_channels(self) -> list[SecondaryChannel]:
        """List of supported Secondary channels.
        Secondary channels can be used to advertise  with the corresponding PHY.
        """
        return await self._adv_manager.get_supported_secondary_channels()  # type: ignore

    async def supported_capabilities(self) -> dict[Capability, Any]:
        """Enumerates Advertising-related controller capabilities useful to the client."""
        return await self._adv_manager.get_supported_capabilities()  # type: ignore

    async def supported_features(self) -> list[Feature]:
        """List  of supported platform features.
        If no features are available on the platform, the SupportedFeatures array will be empty.
        """
        return await self._adv_manager.get_supported_features()  # type: ignore
