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
    Annotated,
    Any,
    Callable,
    Protocol,
    cast,
    overload,
)

from dbus_fast.aio import ProxyInterface, ProxyObject
from dbus_fast.annotations import (
    DBusBool,
    DBusDict,
    DBusInt16,
    DBusSignature,
    DBusStr,
    DBusUInt16,
    DBusUInt32,
)
from dbus_fast.constants import PropertyAccess
from dbus_fast.service import ServiceInterface, _Property, dbus_method, dbus_property
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


DBusArrayString = Annotated[list[str], DBusSignature("as")]
DBusUInt16Dict = Annotated[dict[int, Variant], DBusSignature("a{qv}")]
DBusByteDict = Annotated[dict[int, Variant], DBusSignature("a{yv}")]


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
        self._manufacturer_data: dict[int, Variant] = {}  # uint16 -> bytes
        self._solicit_uuids: list[str] = []
        self._service_data: dict[str, Variant] = {}  # uint16 | str -> bytes
        self._data: dict[int, Variant] = {}  # EXPERIMENTAL # uint8 -> bytes
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

    @dbus_method()
    def Release(self) -> None:
        logger.debug("Released advertisement: %s", self)

    @dbus_property(access=PropertyAccess.READ)
    def Type(self) -> DBusStr:
        """
        Determines the type of advertising packet requested.
        """
        return self._type

    @Type.setter  # type: ignore[no-redef]
    def Type(self, type: DBusStr) -> None:
        self._type = type

    @dbus_property()
    def ServiceUUIDs(self) -> DBusArrayString:
        """
        List of UUIDs to include in the "Service UUID" field of the Advertising Data.
        """
        return self._service_uuids

    @ServiceUUIDs.setter  # type: ignore[no-redef]
    def ServiceUUIDs(self, service_uuids: DBusArrayString) -> None:
        self._service_uuids = service_uuids

    @dbus_property()
    def ManufacturerData(self) -> DBusUInt16Dict:
        """
        Manufacturer Data fields to include in the Advertising Data.
        Keys are the Manufacturer ID to associate with the data.
        """
        return self._manufacturer_data

    @ManufacturerData.setter  # type: ignore[no-redef]
    def ManufacturerData(self, data: DBusUInt16Dict) -> None:
        self._manufacturer_data = data

    @dbus_property()
    def SolicitUUIDs(self) -> DBusArrayString:
        """
        Array of UUIDs to include in "Service Solicitation" Advertisement Data.
        """
        return self._solicit_uuids

    @SolicitUUIDs.setter  # type: ignore[no-redef]
    def SolicitUUIDs(self, uuids: DBusArrayString) -> None:
        self._solicit_uuids = uuids

    @dbus_property()
    def ServiceData(self) -> DBusDict:
        """
        Service Data elements to include. The keys are the UUID to associate with the data.
        """
        return self._service_data

    @ServiceData.setter  # type: ignore[no-redef]
    def ServiceData(self, data: DBusDict) -> None:
        self._service_data = data

    @dbus_property(disabled=True)
    def Data(self) -> DBusByteDict:
        """
        Advertising Data to include.
        Key is the advertising type and value is the data as byte array.
        """
        return self._data

    @Data.setter  # type: ignore[no-redef]
    def Data(self, data: DBusByteDict) -> None:
        self._data = data

    @dbus_property(disabled=True)
    def Discoverable(self) -> DBusBool:
        """
        Advertise as general discoverable.
        When present this will override adapter Discoverable property.
        """
        return self._discoverable

    @Discoverable.setter  # type: ignore[no-redef]
    def Discoverable(self, discoverable: DBusBool) -> None:
        self._discoverable = discoverable

    @dbus_property(disabled=True)
    def DiscoverableTimeout(self) -> DBusUInt16:
        """
        The discoverable timeout in seconds.
        A value of zero means that the timeout is disabled and it will stay in discoverable/limited mode forever.
        """
        return self._discoverable_timeout

    @DiscoverableTimeout.setter  # type: ignore[no-redef]
    def DiscoverableTimeout(self, timeout: DBusUInt16) -> None:
        self._discoverable_timeout = timeout

    @dbus_property()
    def Includes(self) -> DBusArrayString:
        """
        List of features to be included in the advertising packet.
        """
        return self._includes

    @Includes.setter  # type: ignore[no-redef]
    def Includes(self, includes: DBusArrayString) -> None:
        self._includes = includes

    @dbus_property()
    def LocalName(self) -> DBusStr:
        """
        Local name to be used in the advertising report.
        If the string is too big to fit into the packet it will be truncated.
        """
        return self._local_name

    @LocalName.setter  # type: ignore[no-redef]
    def LocalName(self, name: DBusStr) -> None:
        self._local_name = name

    @dbus_property()
    def Appearance(self) -> DBusUInt16:
        """
        Appearance to be used in the advertising report.
        """
        return self._appearance

    @Appearance.setter  # type: ignore[no-redef]
    def Appearance(self, appearance: DBusUInt16) -> None:
        self._appearance = appearance

    @dbus_property()
    def Duration(self) -> DBusUInt16:
        """
        Rotation duration of the advertisement in seconds.
        If there are other applications advertising no duration is set the default is 2 seconds.
        """
        return self._duration

    @Duration.setter  # type: ignore[no-redef]
    def Duration(self, seconds: DBusUInt16) -> None:
        self._duration = seconds

    @dbus_property()
    def Timeout(self) -> DBusUInt16:
        """
        Timeout of the advertisement in seconds.
        This defines the lifetime of the advertisement.
        """
        return self._timeout

    @Timeout.setter  # type: ignore[no-redef]
    def Timeout(self, seconds: DBusUInt16) -> None:
        self._timeout = seconds

    @dbus_property(disabled=True)
    def SecondaryChannel(self) -> DBusStr:
        """
        Secondary channel to be used.
        Primary channel is always set to "1M" except when "Coded" is set.
        """
        return self._secondary_channel

    @SecondaryChannel.setter  # type: ignore[no-redef]
    def SecondaryChannel(self, channel: DBusStr) -> None:
        self._secondary_channel = channel

    @dbus_property(disabled=True)
    def MinInterval(self) -> DBusUInt32:
        """
        Minimum advertising interval to be used by the advertising set, in milliseconds.
        Acceptable values are in the range [20ms, 10,485s].
        If the provided MinInterval is larger than the provided MaxInterval,
        the registration will return failure.
        """
        return self._min_interval

    @MinInterval.setter  # type: ignore[no-redef]
    def MinInterval(self, milliseconds: DBusUInt32) -> None:
        self._min_interval = milliseconds

    @dbus_property(disabled=True)
    def MaxInterval(self) -> DBusUInt32:
        """
        Maximum advertising interval to be used by the advertising set, in milliseconds.
        Acceptable values are in the range [20ms, 10,485s].
        If the provided MinInterval is larger than the provided MaxInterval,
        the registration will return failure.
        """
        return self._max_interval

    @MaxInterval.setter  # type: ignore[no-redef]
    def MaxInterval(self, milliseconds: DBusUInt32) -> None:
        self._max_interval = milliseconds

    @dbus_property(disabled=True)
    def TxPower(self) -> DBusInt16:
        """
        Requested transmission power of this advertising set.
        The provided value is used only if the "CanSetTxPower" feature is enabled on the org.bluez.LEAdvertisingManager(5).
        The provided value must be in range [-127 to +20], where units are in dBm.
        """
        return self._tx_power

    @TxPower.setter  # type: ignore[no-redef]
    def TxPower(self, dbm: DBusInt16) -> None:
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

    @dbus_method()
    def Release(self) -> None:
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
                self._manufacturer_data[self.LEGO_CID].value
            )
            return value
        else:
            return None

    @message.setter
    def message(self, value: PybricksBroadcastData) -> None:
        value = value if isinstance(value, tuple) else (value,)
        message = encode_message(self.channel, *value)
        self._manufacturer_data[self.LEGO_CID] = Variant("ay", message)
        # Notify BlueZ of the changed manufacturer data so the advertisement is updated
        self.emit_properties_changed(
            changed_properties={"ManufacturerData": self._manufacturer_data}
        )

    def __str__(self):
        return f"PybricksBroadcastAdvertisement(channel={self.channel}, data={self.message!r}, timeout={self._timeout})"


class LEAdvertisingManager1(Protocol):
    """Protocol for the 'org.bluez.LEAdvertisingManager1' proxy interface."""

    async def call_register_advertisement(self, path: str, options: dict) -> None:
        """Registers an advertisement object to be sent over the LE Advertising channel.

        The service must implement org.bluez.LEAdvertisement(5) interface.

        Possible errors:

            org.bluez.Error.InvalidArguments
                Indicates that the object has invalid or conflicting properties.
            org.bluez.Error.AlreadyExists
                Indicates the object is already registered.
            org.bluez.Error.InvalidLength
                Indicates that the data provided generates a data packet which is too long.
            org.bluez.Error.NotPermitted
                Indicates the maximum number of advertisement instances has been reached.
        """
        ...

    async def call_unregister_advertisement(self, path: str) -> None:
        """Unregisters an advertisement that has been previously registered using RegisterAdvertisement().

        The object path parameter must match the same value that has been used on registration.

        Possible errors:

            org.bluez.Error.InvalidArguments
            org.bluez.Error.DoesNotExist
        """
        ...

    async def get_active_instances(self) -> int:
        """Number of active advertising instances."""
        ...

    async def get_supported_instances(self) -> int:
        """Number of available advertising instances."""
        ...

    async def get_supported_includes(self) -> list[Include]:
        """List of supported system includes."""
        ...

    async def get_supported_secondary_channels(self) -> list[SecondaryChannel]:
        """List of supported Secondary channels.

        Secondary channels can be used to advertise with the corresponding PHY.
        """
        ...

    async def get_supported_capabilities(self) -> dict[Capability, Any]:
        """Enumerates Advertising-related controller capabilities useful to the client."""
        ...

    async def get_supported_features(self) -> list[Feature]:
        """List of supported platform features.

        If no features are available on the platform, the SupportedFeatures array will be empty."""
        ...


class LEAdvertisingManager:
    """
    Client implementation of the `org.bluez.LEAdvertisementManager1` D-Bus interface.
    """

    INTERFACE_NAME: str = "org.bluez.LEAdvertisingManager1"

    _adv_manager: LEAdvertisingManager1

    def __init__(
        self,
        adapter: ProxyObject | None = None,
        adv_manager: ProxyInterface | None = None,
    ):
        if adapter is None and adv_manager is None:
            raise ValueError("adapter or adv_manager required")

        if adv_manager:
            self._adv_manager = cast(LEAdvertisingManager1, adv_manager)
        elif adapter:
            self._adv_manager = cast(
                LEAdvertisingManager1, adapter.get_interface(self.INTERFACE_NAME)
            )

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
        return await self._adv_manager.call_register_advertisement(adv.path, options)

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
            return await self._adv_manager.call_unregister_advertisement(adv)
        else:
            return await self._adv_manager.call_unregister_advertisement(adv.path)

    async def active_instances(self) -> int:
        """Number of active advertising instances."""
        return await self._adv_manager.get_active_instances()

    async def supported_instances(self) -> int:
        """Number of available advertising instances."""
        return await self._adv_manager.get_supported_instances()

    async def supported_includes(self) -> list[Include]:
        """List of supported system includes."""
        return await self._adv_manager.get_supported_includes()

    async def supported_secondary_channels(self) -> list[SecondaryChannel]:
        """List of supported Secondary channels.
        Secondary channels can be used to advertise  with the corresponding PHY.
        """
        return await self._adv_manager.get_supported_secondary_channels()

    async def supported_capabilities(self) -> dict[Capability, Any]:
        """Enumerates Advertising-related controller capabilities useful to the client."""
        return await self._adv_manager.get_supported_capabilities()

    async def supported_features(self) -> list[Feature]:
        """List  of supported platform features.
        If no features are available on the platform, the SupportedFeatures array will be empty.
        """
        return await self._adv_manager.get_supported_features()
