"""
dbus-next BLE advertisement definitions
"""
import logging
from enum import Enum
from typing import Callable, Dict, List, Set, Union, no_type_check

from dbus_fast.service import ServiceInterface, _Property, dbus_property, method

logger = logging.getLogger(__name__)

# requires Python 3.10
# Type: TypeAlias = Literal["broadcast", "peripheral"]
# Includes: TypeAlias = Literal["tx-power", "appearance", "local-name", "rsi"]
# SecondaryChannel: TypeAlias = Literal["1M", "2M", "Coded"]


class Type(Enum):
    BROADCAST = "broadcast"
    PERIPHERAL = "peripheral"


class Include(Enum):
    TX_POWER = "tx-power"
    APPEARANCE = "appearance"
    LOCAL_NAME = "local-name"
    RSI = "rsi"


class SecondaryChannel(Enum):
    ONE = "1M"
    TWO = "2M"
    CODED = "Coded"


class LEAdvertisement(ServiceInterface):
    """
    Implementation of the org.bluez.LEAdvertisement1 D-Bus interface.

    https://github.com/bluez/bluez/blob/5.64/doc/advertising-api.txt
    """

    INTERFACE_NAME: str = "org.bluez.LEAdvertisement1"

    def __init__(
        self,
        advertising_type: Type,
        name: str,
        index: int = 0,
        includes: Set[Include] = set(),
    ):
        self.index = index
        self.path = f"/org/bluez/{name}/advertisement{index:03}"

        self._type: str = advertising_type.value
        self._service_uuids: List[str] = []
        self._manufacturer_data: Dict[int, bytes] = {}  # uint16 -> bytes
        self._solicit_uuids: List[str] = []
        self._service_data: Dict[Union[str, int], bytes] = {}  # uint16 | str -> bytes
        self._data: Dict[int, bytes] = {}  # EXPERIMENTAL # uint8 -> bytes
        self._discoverable: bool = False  # EXPERIMENTAL
        self._discoverable_timeout: int = 0  # EXPERIMENTAL # uint16
        self._includes: List[str] = [i.value for i in includes]
        self._local_name: str = name
        self._appearance: int = 0x00  # uint16
        self._duration: int = 2  # uint16
        self._timeout: int = 0  # uint16
        self._secondary_channel: str = SecondaryChannel.ONE.value  # EXPERIMENTAL
        self._min_interval: int = 100  # EXPERIMENTAL # uint32
        self._max_interval: int = 1000  # EXPERIMENTAL # uint32
        self._tx_power: int = 20  # EXPERIMENTAL # int16

        super().__init__(self.INTERFACE_NAME)

    def _enable_props(self, *prop_names: str):
        """
        Enables the given properties.

        This should be used by subclasses to opt-into experimental properties.

        Args:
            prop_names: List of D-Bus property names to enable.

        Raises:
            ValueError: If an unknown property was passed.
        """
        for prop_name in prop_names:
            prop: _Property = next(
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

        Args:
            prop_names: List of D-Bus property names to disable.

        Raises:
            ValueError: If an unknown property was passed.
        """
        for prop_name in prop_names:
            prop: _Property = next(
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

    @dbus_property()
    @no_type_check
    def Type(self) -> "s":  # type: ignore # noqa: F821
        return self._type

    @Type.setter
    @no_type_check
    def Type(self, type: "s"):  # type: ignore  # noqa: F821
        self._type = type

    @dbus_property()
    @no_type_check
    def ServiceUUIDs(self) -> "as":  # type: ignore # noqa: F821 F722
        return self._service_uuids

    @ServiceUUIDs.setter
    @no_type_check
    def ServiceUUIDs(self, service_uuids: "as"):  # type: ignore # noqa: F821 F722
        self._service_uuids = service_uuids

    @dbus_property()
    @no_type_check
    def ManufacturerData(self) -> "a{qv}":  # type: ignore # noqa: F821 F722
        return self._manufacturer_data

    @ManufacturerData.setter
    @no_type_check
    def ManufacturerData(self, data: "a{qv}"):  # type: ignore # noqa: F821 F722
        self._manufacturer_data = data

    @dbus_property()
    @no_type_check
    def SolicitUUIDs(self) -> "as":  # type: ignore # noqa: F821 F722
        return self._solicit_uuids

    @SolicitUUIDs.setter
    @no_type_check
    def SolicitUUIDs(self, uuids: "as"):  # type: ignore # noqa: F821 F722
        self._solicit_uuids = uuids

    @dbus_property()
    @no_type_check
    def ServiceData(self) -> "a{sv}":  # type: ignore # noqa: F821 F722
        return self._service_data

    @ServiceData.setter
    @no_type_check
    def ServiceData(self, data: "a{sv}"):  # type: ignore # noqa: F821 F722
        self._service_data = data

    @dbus_property(disabled=True)
    @no_type_check
    def Data(self) -> "a{yv}":  # type: ignore # noqa: F821 F722
        return self._data

    @Data.setter
    @no_type_check
    def Data(self, data: "a{yv}"):  # type: ignore # noqa: F821 F722
        self._data = data

    @dbus_property(disabled=True)
    @no_type_check
    def Discoverable(self) -> "b":  # type: ignore # noqa: F821 F722
        return self._discoverable

    @Discoverable.setter
    @no_type_check
    def Discoverable(self, discoverable: "b"):  # type: ignore # noqa: F821 F722
        self._discoverable = discoverable

    @dbus_property(disabled=True)
    @no_type_check
    def DiscoverableTimeout(self) -> "q":  # type: ignore # noqa: F821 F722
        return self._discoverable_timeout

    @DiscoverableTimeout.setter
    @no_type_check
    def DiscoverableTimeout(self, timeout: "q"):  # type: ignore # noqa: F821 F722
        self._discoverable_timeout = timeout

    @dbus_property()
    @no_type_check
    def Includes(self) -> "as":  # type: ignore # noqa: F821 F722
        return self._includes

    @Includes.setter
    @no_type_check
    def Includes(self, includes: "as"):  # type: ignore # noqa: F821 F722
        self._includes = includes

    @dbus_property()
    @no_type_check
    def LocalName(self) -> "s":  # type: ignore # noqa: F821 N802
        return self._local_name

    @LocalName.setter
    @no_type_check
    def LocalName(self, name: "s"):  # type: ignore # noqa: F821 N802
        self._local_name = name

    @dbus_property()
    @no_type_check
    def Appearance(self) -> "q":  # type: ignore # noqa: F821 N802
        return self._appearance

    @Appearance.setter
    @no_type_check
    def Appearance(self, appearance: "q"):  # type: ignore # noqa: F821 N802
        self._appearance = appearance

    @dbus_property()
    @no_type_check
    def Duration(self) -> "q":  # type: ignore # noqa: F821 N802
        return self._duration

    @Duration.setter
    @no_type_check
    def Duration(self, seconds: "q"):  # type: ignore # noqa: F821 N802
        self._duration = seconds

    @dbus_property()
    @no_type_check
    def Timeout(self) -> "q":  # type: ignore # noqa: F821 N802
        return self._timeout

    @Timeout.setter
    @no_type_check
    def Timeout(self, seconds: "q"):  # type: ignore # noqa: F821 N802
        self._timeout = seconds

    @dbus_property(disabled=True)
    @no_type_check
    def SecondaryChannel(self) -> "s":  # type: ignore # noqa: F821 N802
        return self._secondary_channel

    @SecondaryChannel.setter
    @no_type_check
    def SecondaryChannel(self, channel: "q"):  # type: ignore # noqa: F821 N802
        self._secondary_channel = channel

    @dbus_property(disabled=True)
    @no_type_check
    def MinInterval(self) -> "u":  # type: ignore # noqa: F821 N802
        return self._min_interval

    @MinInterval.setter
    @no_type_check
    def MinInterval(self, milliseconds: "u"):  # type: ignore # noqa: F821 N802
        self._min_interval = milliseconds

    @dbus_property(disabled=True)
    @no_type_check
    def MaxInterval(self) -> "u":  # type: ignore # noqa: F821 N802
        return self._max_interval

    @MaxInterval.setter
    @no_type_check
    def MaxInterval(self, milliseconds: "u"):  # type: ignore # noqa: F821 N802
        self._max_interval = milliseconds

    @dbus_property(disabled=True)
    @no_type_check
    def TxPower(self) -> "n":  # type: ignore # noqa: F821 N802
        return self._tx_power

    @TxPower.setter
    @no_type_check
    def TxPower(self, dbm: "n"):  # type: ignore # noqa: F821 N802
        self._tx_power = dbm


class BroadcastAdvertisement(LEAdvertisement):
    def __init__(
        self,
        name: str,
        index: int = 0,
        on_release: Callable[[int], None] = lambda i: None,
    ):
        super().__init__(
            Type.BROADCAST,
            name,
            index,
            # set([Include.LOCAL_NAME]),
        )

        self.on_release = on_release

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
        self.on_release(self.index)
