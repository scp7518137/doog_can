"""Provide helpers to create and tear down CAN bus transports."""
import can
from .constants import (
    CAN_BITRATE_BPS,
    COMM_TIMEOUT_MS,
)

def can_init(mycan) -> can.BusABC:
    """Open the real CAN bus interface (socketcan channel can0).
    
    Args:
        can: "can0" / "can1"

    Returns:
        The initialized CAN bus instance.
    """
    bus = can.Bus(channel = mycan, interface="socketcan")
    return bus

def vbus_init(name) -> tuple[can.BusABC, can.BusABC]:
    """Create a pair of virtual CAN buses sharing the same channel.

    Args:
        name: Name of the virtual channel both buses connect to.

    Returns:
        A tuple of (send bus, receive bus) on the shared virtual channel.
    """
    bus_send = can.Bus(interface="virtual", channel=name)
    bus_receive = can.Bus(interface="virtual", channel=name)
    return bus_send, bus_receive

def vbus_close(bus:can.BusABC) -> None:
    """Shut down a virtual CAN bus.

    Args:
        bus: The CAN bus instance to close.
    """
    bus.shutdown